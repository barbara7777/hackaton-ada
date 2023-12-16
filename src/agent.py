import dotenv
import datetime

from langchain import hub
from langchain.chat_models import ChatOpenAI
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.tools.render import render_text_description
from langchain.agents import AgentType, Tool, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.utilities import SerpAPIWrapper
from langchain.agents.format_scratchpad import format_log_to_messages
from langchain.agents.output_parsers import JSONAgentOutputParser
from langchain.agents import AgentExecutor

from rtv_tool import RtvTool, BicikeljInfoTool

SYSTEM_PROMPT = """Danes je {date}. Si prijazna pomočnica po imenu Delfinček.
Narejena si da pomagaš ljudem pri različnih problemih. Od odgovarjanja na preprosta vsakodnevna vprašanja do pomoči pri branju novic in pregledu nad razpoložljivostjo koles v Ljubljani.
Za razpoložljivost koles in prebiranje novic uporabljaš orodja. Za odgovarjanje na vprašanja pa uporabljaš svoje znanje. Sposobna si prebirati velike količine podatkov in iz njih izluščiti pomembne informacije.
Na vsa uporabnikov vhod si sposobna odgovoriti v slovenskem jeziku na razumljiv in naraven način. Vedno ponujaš smiselne in relevantne odgovore glede na temo uporabnikovega vhoda. Odgovarjaj krakto in jedernato.

ORODJA:
-------
Sposobna si uporabljat naslednja orodja za pomoč uporabnikom:

{tools}

NAVODILA ZA FORMIRANJE ODGOVORA:
--------------------------------
Ko odgovarjaš na uporabnikov vhod, odgovori v enem od naslednjih formatov:

**Možnost 1:**
Uporabi to markdown shemo ko želiš uporabit orodje:

```json
{{
    "action": string, \ action mora biti eno izmed orodji: {tool_names}
    "action_input": string \ Vhod za orodje.
}}
```

**Možnost 2:**
Uporabi to markdown shemo ko želiš odgovorit uporabniku:

```json
{{
    "action": "Final Answer",
    "action_input": string \ Odogovor uporabniku v slovenščini.
}}
```
"""

INPUT_PROMPT = """UPORABNIKOV VHOD:
-----------------
Tu je uporabnikov vhod (odgovori z markdown shemo json bloka z eno akcijo in nič drugega):

{{{input}}}
"""

TEMPLATE_TOOL_RESPONSE = """{observation}"""


def search(tmp):
    return "No data"


def get_tools():
    tools = [RtvTool(), BicikeljInfoTool()]
    return tools


def init_agent():
    prompt = hub.pull("hwchase17/react-chat-json")
    chat_model = ChatOpenAI(temperature=0, model="gpt-4-1106-preview")
    prompt.messages[0].prompt.input_variables = ["date", "tools", "tool_names"]
    prompt.messages[0].prompt.template = SYSTEM_PROMPT
    prompt.messages[2].prompt.input_variables = ["input"]
    prompt.messages[2].prompt.template = INPUT_PROMPT
    tools = get_tools()
    prompt = prompt.partial(
        tools=render_text_description(tools),
        tool_names=", ".join([t.name for t in tools]),
        date=datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
    )
    chat_model_with_stop = chat_model.bind(stop=["\nKorak"])

    agent = (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_log_to_messages(
                x["intermediate_steps"], template_tool_response=TEMPLATE_TOOL_RESPONSE
            ),
            "chat_history": lambda x: x["chat_history"],
        }
        | prompt
        | chat_model_with_stop
        | JSONAgentOutputParser()
    )

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, memory=memory)

    return agent_executor


if __name__ == "__main__":
    dotenv.load_dotenv()
    agent_ex = init_agent()
    print(agent_ex.invoke({"input": "Kaj je portal OPSI?"})["output"])
