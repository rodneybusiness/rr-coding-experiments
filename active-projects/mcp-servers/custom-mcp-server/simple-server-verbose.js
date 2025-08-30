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
  console.log(`Received request: ${req.method} ${req.url}`);
  
  // Enable CORS for all requests
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    // Handle CORS preflight requests
    res.writeHead(204);
    res.end();
    return;
  }

  // Respond to all POST requests with the tool list
  if (req.method === 'POST') {
    // First try to parse the body
    let body = '';
    req.on('data', chunk => {
      body += chunk.toString();
    });
    
    req.on('end', () => {
      try {
        console.log(`Request body: ${body}`);
        let data = {};
        
        try {
          data = JSON.parse(body);
        } catch (e) {
          console.log(`Failed to parse JSON: ${e.message}`);
        }
        
        // If this looks like a tools request
        if (req.url.includes('/tools') || req.url === '/') {
          res.writeHead(200, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ tools: [thinkTool] }));
          return;
        }
        
        // If this looks like an execute request
        if (req.url.includes('/execute') || 
            (data.tool === 'think' && data.parameters && data.parameters.thought)) {
          
          const thought = data.parameters?.thought || "No thought provided";
          console.log(`THOUGHT: ${thought}`);
          
          res.writeHead(200, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ 
            result: `Thought recorded: ${thought}` 
          }));
          return;
        }
        
        // Default response for unknown POST requests
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ 
          message: "Server received POST request",
          tools: [thinkTool]
        }));
      } catch (error) {
        console.error(`Error handling request: ${error.message}`);
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ 
          error: 'Server error: ' + error.message 
        }));
      }
    });
    return;
  }

  // Handle any GET request
  if (req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ 
      message: "Custom MCP server is running",
      tools: [thinkTool]
    }));
    return;
  }

  // Handle any other request
  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ error: 'Not found' }));
});

// Start the server on a specific port
const PORT = 8080;
server.listen(PORT, () => {
  console.log(`Custom MCP server is running on http://localhost:${PORT}`);
  console.log(`Available tools: think`);
});