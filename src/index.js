const express = require("express");
const { spawn } = require("child_process");
const path = require("path");
const http = require("http");
const { Server } = require("socket.io");
const fs = require("fs");
const cors = require('cors');

const app = express();
const server = http.createServer(app);

app.use(cors({
  origin: 'http://localhost:3000' // Replace with your frontend URL
}));

const io = new Server(server, {
  cors: {
    origin: "http://localhost:3000", // Replace with your frontend's URL
    methods: ["GET", "POST"],
  }
});

const PORT = 3001;

let processes = {
  monitor: null,
  bot_monitor: null,
};

// Serve frontend (index.html will go inside /public)
app.use(express.static(path.join(__dirname, "..", "public")));



// Function to run python scripts
function runPythonScript(name, scriptFile) {
  if (processes[name]) {
    return { error: `${name} is already running.` };
  }

  const scriptPath = path.join(__dirname, "..", scriptFile);

  // Run from project root so session files are found
  const child = spawn("python", [scriptPath], {
    cwd: path.join(__dirname, ".."),
  });

  processes[name] = child;

  child.stdout.on("data", (data) => {
    console.log(`[${name}] ${data.toString()}`);
  });

  child.stderr.on("data", (data) => {
    console.error(`[${name} ERROR] ${data.toString()}`);
  });

  child.on("close", (code) => {
    console.log(`${name} exited with code ${code}`);
    processes[name] = null;
  });

  return { success: `${name} started` };
}

// APIs
app.get("/start-monitor", (req, res) => {
  res.send(runPythonScript("monitor", "monitor.py"));
});

app.get("/start-bot-monitor", (req, res) => {
  res.send(runPythonScript("bot_monitor", "bot_monitor.py"));
});

app.get("/stop-monitor", (req, res) => {
  if (processes.monitor) {
    processes.monitor.kill("SIGTERM");
    processes.monitor = null;
    return res.send({ success: "monitor.py stopped" });
  }
  res.send({ error: "monitor.py is not running" });
});

app.get("/stop-bot-monitor", (req, res) => {
  if (processes.bot_monitor) {
    processes.bot_monitor.kill("SIGTERM");
    processes.bot_monitor = null;
    return res.send({ success: "bot_monitor.py stopped" });
  }
  res.send({ error: "bot_monitor.py is not running" });
});

// Watch logs and send new updates to frontend
function watchLogFile(filePath, eventName) {
  let lastSize = fs.existsSync(filePath) ? fs.statSync(filePath).size : 0;

  // Watch for file changes
  fs.watch(filePath, (eventType, filename) => {
    if (eventType === 'change') {
      const currentSize = fs.statSync(filePath).size;
      const newBytes = currentSize - lastSize;

      if (newBytes > 0) {
        const readStream = fs.createReadStream(filePath, { start: lastSize });
        let newContent = '';

        readStream.on('data', (chunk) => {
          newContent += chunk.toString();
        });

        readStream.on('end', () => {
          io.emit(eventName, newContent);
          lastSize = currentSize;
        });
      }
    }
  });

  // Also send initial content when a client connects
  io.on('connection', (socket) => {
    fs.readFile(filePath, "utf8", (err, data) => {
      if (!err) {
        socket.emit(eventName, data);
      }
    });
  });
}

// watch alerts.log and bot_alerts.log
watchLogFile(path.join(__dirname, "..", "alerts.log"), "alertsLogUpdate");
watchLogFile(path.join(__dirname, "..", "bot_alerts.log"), "botAlertsLogUpdate");

server.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
});