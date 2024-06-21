import express from "express";
import fetch from "node-fetch";
import cors from "cors";
import dotenv from "dotenv";
import https from "https";
import { readFileSync } from "fs";
import path from "path";
import { dirname } from "path";
import { fileURLToPath } from "url";
import { spawn } from "child_process";
import { SUBJECT_DATA } from "./utils/constants.js";

dotenv.config();

const httpsAgent = new https.Agent({
  rejectUnauthorized: false,
});

const API_KEY = "62fd09ca0e4bda109687a49faee18bcd"  //process.env.API_KEY;

const app = express();
const PORT = process.env.PORT || 3000;

app.use(
  cors({
    origin: "*",
    methods: ["GET", "POST"], // Specify the methods allowed
    allowedHeaders: ["Content-Type", "Authorization", "ORGID", "apiKey"], // Added 'apiKey' to allowed headers
  })
);
app.use(express.json());

app.get("/studentDetails", async (req, res) => {
  const { email, subject } = req.query;
  console.log("Received email:", email);
  console.log("Received subject:", subject);

  try {
    // Dynamic subject handling
    let classId, testId;
    const subjectData = SUBJECT_DATA[subject];
    if (subjectData) {
      [classId, testId] = subjectData;
    } else {
      return res.status(400).json({ message: `Subject not found: ${subject}` });
    }

    const studentApiUrl = `https://lms.academically.com/nuSource/api/v1/student/search?institution_id=4502&student_email=${email}`;
    const headers = {
      apiKey: API_KEY,
      ORGID: "5735",
    };

    const studentResponse = await fetch(studentApiUrl, {
      method: "GET",
      headers: headers,
      agent: httpsAgent,
    });
    if (!studentResponse.ok) {
      throw new Error(
        `API call failed1 with status: ${studentResponse.status}`
      );
    }
    const studentData = await studentResponse.json();
    console.log("Student API data:", studentData);

    const marksApiUrl = `https://lms.academically.com/nuSource/api/v1/exercises/${testId}/attemptlist?class_id=${classId}&user_id=${studentData.user_details[0].student_id}&is_quiz=false`;
    const marksResponse = await fetch(marksApiUrl, {
      method: "GET",
      headers: headers,
      agent: httpsAgent,
    });
    if (!marksResponse.ok) {
      throw new Error(`API call failed2 with status: ${marksResponse.status}`);
    }
    const marksData = await marksResponse.json();
    console.log("Marks API data:", marksData);

    if (marksData.exercises.length === 0) {
      return res.json({
        userDetails: studentData.user_details,
        message: "No attempts Found",
      });
    }

    res.json({
      userDetails: studentData.user_details,
      userMarks: marksData.exercises,
    });
  } catch (error) {
    console.error("Error during API call:", error);
    res.status(500).json({ error: error.message });
  }
});

const __dirname = dirname(fileURLToPath(import.meta.url));
app.get("/", (req, res) => {
  const indexPath = path.join(__dirname, "index.html");
  const indexContent = readFileSync(indexPath, "utf-8");
  res.send(indexContent);
});


let lock = false;
const queue = [];

app.post("/run-script", (req, res) => {
  queue.push({ req, res });
  processQueue();
});


function processQueue() {
  if (lock || queue.length === 0) {
    return;
  }

  lock = true;
  const { req, res } = queue.shift();
  const { studentId, subject } = req.body;

  try {
    const pythonExecutable = process.env.PYTHON_EXECUTABLE_PATH;
    const scriptPath = path.join(__dirname, "generate.py");
    const pythonProcess = spawn(pythonExecutable, [
      scriptPath,
      studentId,
      subject,
    ]);

    let output = "";
    pythonProcess.stdout.on("data", (data) => {
      output += data.toString();
    });

    pythonProcess.stderr.on("data", (data) => {
      console.error(`stderr: ${data}`);
      res.status(500).send(`Error: ${data}`);
      lock = false;
      processQueue();
    });

    pythonProcess.on("close", (code) => {
      lock = false;
      processQueue();
      if (code === 0) {
        downloadFinalReport(res);
      } else {
        res.status(500).send(`Process exited with code: ${code}`);
      }
    });
  } catch (error) {
    console.error("Error during API call:", error);
    res.status(500).json({ error: error.message });
    lock = false;
    processQueue();
  }
}

const downloadFinalReport = (res) => {
  const file = path.join(__dirname, "..", "assets/pdfs/final_report.pdf");
  res.download(file, (err) => {
    if (err) {
      console.error("Error downloading file:", err);
      res.status(500).send("Error downloading file.");
    }
  });
}

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
