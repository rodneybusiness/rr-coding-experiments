import { createServer } from '@modelcontextprotocol/server';

// Define the "think" tool
const thinkTool = {
  "name": "think",
  "description": "Use the tool to think about something. It will not obtain new information or change the database, but just append the thought to the log. Use it when complex reasoning or some cache memory is needed.",
  "input_schema": {
    "type": "object",
    "properties": {
      "thought": {
        "type": "string",
        "description": "A thought to think about."
      }
    },
    "required": ["thought"]
  },
  // Handler function for the tool
  async handler(params) {
    const { thought } = params;
    console.log(`THOUGHT: ${thought}`);
    return { result: `Thought recorded: ${thought}` };
  }
};

// Create and start the server
const server = createServer({
  tools: [thinkTool],
});

server.listen(0, () => {
  const address = server.address();
  console.log(`MCP server listening on port ${address.port}`);
});