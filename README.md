UGANDA AGRICULTURAL TRADERS BUSINESS ASSISTANT
Project: Building a Business Assistant Chatbot for Agricultural Traders in Uganda. 


We employ a Langgraph Flow chart to show how the Ai will flow.

And a High-Level-Architectural-diagram




./assets/flow_chart.png
./assests/high_arc_diagram.png

This application is a smart chatbot designed to assist Ugandan agricultural traders with business-related queries. It is built using Langgraph, multi-step agent applications. The core of this application's architecture is a Supervisor/Worker pattern, which enables the system to intelligently route a user's request to the appropriate tool.

The Web Agent powered by Tavily consists of three main components: the language model, a set of web tools, and a system prompt. The language model(chatgroq) serves as the agent's "brain", while the web tools such as Tavily search and call_tool allow the agent to interact with and gather information from the allowed sites and intepret, generate reports among others. The system prompt guides the agent's behaviour, explaining how and when to use each tool to accomplish its research goals.

The Architecture: Supervisor and Workers

The Supervisor Agent(Chatbot)
1. Receive the Query: Take the User's initial question
2. Analyze intent: Use a powerful LLM to understand what the user wants to achieve.
3. Delegate: Decide which specialized worker agent is best suited to fulfill the request.
The Supervisor doesn't perform a web search or database lookup itself; it delegates these tasks to specialized "workers".

The Worker Agents(Tools)
The worker agents are the specialized tools that the supervisor can call upon. Each worker is an expert at a single task. In  this application, our primary workers are:

1. tavily_search: Finds the latest information on the web. It is used when a user's query requires up to date or external data.

2. db_lookup_node: An expert in querying our internal database to find previously answered questions. The Supervisor  calls this worker to save time and resources by avoiding unnecessary web searches.

3. data_analysis_agent: Performs complex calculations and analyzes numerical data. It uses Python interpreter tool to process requests.

4. report_generation_agent: This worker specialises in synthesizing information into a structured report or summary, taking facts from other agents and formatting them for easy consumption.

5. database_query_agent: A more advanced worker that can execute specific SQL queries to retrieve or update information in the internal database.

Application Flow
The graph priotizes using internal knowledge base before resorting to external knowledge.

1. Start: A user's query enters the graph

2. Database Lookup: The query first goes to the db_lookup_node. This checks the internal database to see if the question has been answered before.

3. Conditional Routing: The graph checks the result of the lookup.
* If a cached answer is found, the graph immediately routes to END and presents the answer to the user.
* If no answer is found, the query is passed to the chatbot(Supervisor) node.

4. Supervisor Analysis: The chatbot receives the query and decides if a tool call is necessary whether it can respond directly or call one of its specialized worker agents.

5. Tool Execution: If Supervisor calls a worker tool, the graph is routed to the tool_call node. This node executes the specific task whatever is called.

6. Synthesize Response: Once the tool_call node returns the results, the graph loops back to the chatbot(Supervisor). The Supervisor uses the results to formulate a final, comprehensive answer for the user.

7. End: The process concludes with a final response to the User.
















