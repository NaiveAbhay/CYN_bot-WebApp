
// const express = require("express");
// const { spawn } = require("child_process");
// const path = require("path");
// const http = require("http");
// const { Server } = require("socket.io");
// const fs = require("fs");
// const cors = require('cors');

// const app = express();
// const server = http.createServer(app);

// app.use(cors({
//   origin: 'http://localhost:3000'
// }));

// // Enable JSON body parsing
// app.use(express.json());

// const io = new Server(server, {
//   cors: {
//     origin: "http://localhost:3000",
//     methods: ["GET", "POST"],
//   }
// });

// const PORT = 3001;

// let processes = {
//   monitor: null,
//   bot_monitor: null,
// };

// // Serve frontend (index.html will go inside /public)
// app.use(express.static(path.join(__dirname, "..", "public")));

// // Function to run python scripts
// function runPythonScript(name, scriptFile, args = []) {
//   if (processes[name]) {
//     return { error: `${name} is already running.` };
//   }

//   const scriptPath = path.join(__dirname, "..", scriptFile);
//   const child = spawn("python", [scriptPath, ...args], {
//     cwd: path.join(__dirname, ".."),
//   });

//   processes[name] = child;

//   child.stdout.on("data", (data) => {
//     console.log(`[${name}] ${data.toString()}`);
//   });

//   child.stderr.on("data", (data) => {
//     console.error(`[${name} ERROR] ${data.toString()}`);
//   });

//   child.on("close", (code) => {
//     console.log(`${name} exited with code ${code}`);
//     processes[name] = null;
//   });

//   return { success: `${name} started` };
// }

// // Existing APIs (unchanged)
// app.get("/start-monitor", (req, res) => {
//   res.send(runPythonScript("monitor", "monitor.py"));
// });

// app.get("/stop-monitor", (req, res) => {
//   if (processes.monitor) {
//     processes.monitor.kill("SIGTERM");
//     processes.monitor = null;
//     return res.send({ success: "monitor.py stopped" });
//   }
//   res.send({ error: "monitor.py is not running" });
// });

// // NEW DYNAMIC API FOR BOT MONITOR
// app.post("/start-bot-monitor-dynamic", (req, res) => {
//   const { users } = req.body; // Expects an array of users in the request body
//   if (!users || !Array.isArray(users) || users.length === 0) {
//     return res.status(400).send({ error: "No users provided." });
//   }

//   // Pass each user as a separate command-line argument
//   const args = users; 
//   res.send(runPythonScript("bot_monitor", "bot_monitor.py", args));
// });

// // Existing stop API (unchanged)
// app.get("/stop-bot-monitor", (req, res) => {
//   if (processes.bot_monitor) {
//     processes.bot_monitor.kill("SIGTERM");
//     processes.bot_monitor = null;
//     return res.send({ success: "bot_monitor.py stopped" });
//   }
//   res.send({ error: "bot_monitor.py is not running" });
// });

// // Watch logs and send new updates to frontend (unchanged)
// function watchLogFile(filePath, eventName) {
//   let lastSize = fs.existsSync(filePath) ? fs.statSync(filePath).size : 0;
//   fs.watch(filePath, (eventType, filename) => {
//     if (eventType === 'change') {
//       const currentSize = fs.statSync(filePath).size;
//       const newBytes = currentSize - lastSize;
//       if (newBytes > 0) {
//         const readStream = fs.createReadStream(filePath, { start: lastSize });
//         let newContent = '';
//         readStream.on('data', (chunk) => {
//           newContent += chunk.toString();
//         });
//         readStream.on('end', () => {
//           io.emit(eventName, newContent);
//           lastSize = currentSize;
//         });
//       }
//     }
//   });

//   io.on('connection', (socket) => {
//     fs.readFile(filePath, "utf8", (err, data) => {
//       if (!err) {
//         socket.emit(eventName, data);
//       }
//     });
//   });
// }
//hii
// watchLogFile(path.join(__dirname, "..", "alerts.log"), "alertsLogUpdate");
// watchLogFile(path.join(__dirname, "..", "bot_alerts.log"), "botAlertsLogUpdate");

// server.listen(PORT, () => {
//   console.log(`🚀 Server running on http://localhost:${PORT}`);
// });
const express = require("express");
const { spawn } = require("child_process");
const path = require("path");
const http = require("http");
const { Server } = require("socket.io");
const fs = require("fs");
const cors = require("cors");
const dotenv = require("dotenv");

dotenv.config();

const app = express();
const server = http.createServer(app);

const FRONTEND_URL =  process.env.FRONTEND_URL;
const PORT = process.env.PORT || 3001;

app.use(
  cors({
    origin: FRONTEND_URL,
    methods: ["GET", "POST", "PUT", "DELETE"],
    credentials: true,
  })
);

app.use(express.json());

const io = new Server(server, {
  cors: {
    origin: FRONTEND_URL,
    methods: ["GET", "POST"],
    credentials: true,
  },
});

let processes = {
  monitor: null,
  bot_monitor: null,
};

// Serve frontend (from /public in root)
app.use(express.static(path.join(__dirname, "public")));

// Function to run python scripts
function runPythonScript(name, scriptFile, args = []) {
  if (processes[name]) {
    return { error: `${name} is already running.` };
  }

  const scriptPath = path.join(__dirname, scriptFile);
  const child = spawn("python", [scriptPath, ...args], {
    cwd: __dirname,
  });

  processes[name] = child;

  child.stdout.on("data", (data) => console.log(`[${name}] ${data.toString()}`));
  child.stderr.on("data", (data) => console.error(`[${name} ERROR] ${data.toString()}`));

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

app.get("/stop-monitor", (req, res) => {
  if (processes.monitor) {
    processes.monitor.kill("SIGTERM");
    processes.monitor = null;
    return res.send({ success: "monitor.py stopped" });
  }
  res.send({ error: "monitor.py is not running" });
});

app.post("/start-bot-monitor-dynamic", (req, res) => {
  const { users } = req.body;
  if (!users || !Array.isArray(users) || users.length === 0) {
    return res.status(400).send({ error: "No users provided." });
  }
  res.send(runPythonScript("bot_monitor", "bot_monitor.py", users));
});

app.get("/stop-bot-monitor", (req, res) => {
  if (processes.bot_monitor) {
    processes.bot_monitor.kill("SIGTERM");
    processes.bot_monitor = null;
    return res.send({ success: "bot_monitor.py stopped" });
  }
  res.send({ error: "bot_monitor.py is not running" });
});

// Watch logs
function watchLogFile(filePath, eventName) {
  let lastSize = fs.existsSync(filePath) ? fs.statSync(filePath).size : 0;

  fs.watch(filePath, (eventType) => {
    if (eventType === "change") {
      const currentSize = fs.statSync(filePath).size;
      const newBytes = currentSize - lastSize;

      if (newBytes > 0) {
        const readStream = fs.createReadStream(filePath, { start: lastSize });
        let newContent = "";

        readStream.on("data", (chunk) => (newContent += chunk.toString()));
        readStream.on("end", () => {
          io.emit(eventName, newContent);
          lastSize = currentSize;
        });
      }
    }
  });

  io.on("connection", (socket) => {
    fs.readFile(filePath, "utf8", (err, data) => {
      if (!err) socket.emit(eventName, data);
    });
  });
}

// Updated log watchers (from root)
watchLogFile(path.join(__dirname, "alerts.log"), "alertsLogUpdate");
watchLogFile(path.join(__dirname, "bot_alerts.log"), "botAlertsLogUpdate");

server.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
});
