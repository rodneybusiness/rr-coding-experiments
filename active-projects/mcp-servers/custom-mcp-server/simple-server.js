// Simple custom MCP server that implements a "think" tool
// This is a standalone implementation that doesn't require external packages

import http from 'http';

// Define the "think" tool
const thinkTool = {
  name: "think",
  description: "Use the tool to think about something. It will not obtain new information or change the database, but just append the thought to the log. Use it when complex reasoning or some cache memory is needed.",
  parameters: {
    type: "object",
    properties: {
      thought: {
        type: "string",
        description: "A thought to think about."
      }
    },
    required: ["thought"]
  }
};

// Create a simple HTTP server
const server = http.createServer((req, res) => {
  if (req.method === 'OPTIONS') {
    // Handle CORS preflight requests
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    });
    res.end();
    return;
  }

  if (req.method === 'POST' && req.url === '/mcp/v1/tools') {
    // Return the list of available tools
    res.writeHead(200, { 
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*' 
    });
    res.end(JSON.stringify({ tools: [thinkTool] }));
    return;
  }

  if (req.method === 'POST' && req.url === '/mcp/v1/execute') {
    // Handle tool execution
    let body = '';
    req.on('data', chunk => {
      body += chunk.toString();
    });
    req.on('end', () => {
      try {
        const data = JSON.parse(body);
        
        if (data.tool === 'think' && data.parameters && data.parameters.thought) {
          const thought = data.parameters.thought;
          console.log(`THOUGHT: ${thought}`);
          
          res.writeHead(200, { 
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*' 
          });
          res.end(JSON.stringify({ 
            result: `Thought recorded: ${thought}` 
          }));
        } else {
          res.writeHead(400, { 
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*' 
          });
          res.end(JSON.stringify({ 
            error: 'Invalid tool or parameters' 
          }));
        }
      } catch (error) {
        res.writeHead(500, { 
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*' 
        });
        res.end(JSON.stringify({ 
          error: 'Server error: ' + error.message 
        }));
      }
    });
    return;
  }

  // Handle any other request
  res.writeHead(404, { 
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*' 
  });
  res.end(JSON.stringify({ error: 'Not found' }));
});

// Start the server on a specific port
const PORT = 8080;
server.listen(PORT, () => {
  console.log(`Custom MCP server is running on http://localhost:${PORT}`);
  console.log(`Available tools: think`);
});