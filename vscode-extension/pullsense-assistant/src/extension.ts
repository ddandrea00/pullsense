import * as vscode from "vscode";

// Configuration for your PullSense API
const PULLSENSE_API_URL = "http://localhost:8000"; // Your local backend

// Global variables for inline analysis
let analysisTimeout: NodeJS.Timeout | undefined;
let inlineAnalysisPanel: vscode.WebviewPanel | undefined;
const ANALYSIS_DELAY = 2000; // Wait 2 seconds after user stops typing

export function activate(context: vscode.ExtensionContext) {
  console.log("PullSense Code Assistant is now active!");

  // Command 1: Analyze Current File
  const analyzeFileCommand = vscode.commands.registerCommand(
    "pullsense-assistant.analyzeCurrentFile",
    async () => {
      const editor = vscode.window.activeTextEditor;

      if (!editor) {
        vscode.window.showErrorMessage("No active file to analyze");
        return;
      }

      const document = editor.document;
      const fileName = document.fileName;
      const fileContent = document.getText();

      vscode.window.showInformationMessage(`Analyzing ${fileName}...`);

      try {
        // Call your PullSense API here
        const analysis = await analyzeCode(fileContent, fileName);
        showAnalysisResults(analysis, fileName);
      } catch (error) {
        vscode.window.showErrorMessage(`Failed to analyze file: ${error}`);
      }
    }
  );

  // Command 2: Analyze Pull Request
  const analyzePRCommand = vscode.commands.registerCommand(
    "pullsense-assistant.analyzePR",
    async () => {
      vscode.window.showInformationMessage("Opening PR analysis...");

      // Get Git repository info
      const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
      if (!workspaceFolder) {
        vscode.window.showErrorMessage("No workspace folder found");
        return;
      }

      // TODO: Implement PR analysis logic
      vscode.window.showInformationMessage("PR analysis coming soon!");
    }
  );

  // Command 3: Open Dashboard
  const dashboardCommand = vscode.commands.registerCommand(
    "pullsense-assistant.showDashboard",
    () => {
      const panel = vscode.window.createWebviewPanel(
        "pullsenseDashboard",
        "PullSense Dashboard",
        vscode.ViewColumn.Two,
        {
          enableScripts: true,
        }
      );

      panel.webview.html = getDashboardHtml();
    }
  );

  // Command 4: Toggle Inline Analysis
  const toggleInlineCommand = vscode.commands.registerCommand(
    "pullsense-assistant.toggleInlineAnalysis",
    () => {
      if (inlineAnalysisPanel) {
        inlineAnalysisPanel.dispose();
        inlineAnalysisPanel = undefined;
        vscode.window.showInformationMessage("Inline analysis disabled");
      } else {
        createInlineAnalysisPanel();
        vscode.window.showInformationMessage("Inline analysis enabled");
      }
    }
  );

  // Real-time code analysis
  const documentChangeListener = vscode.workspace.onDidChangeTextDocument(
    (event) => {
      const editor = vscode.window.activeTextEditor;

      // Only analyze if this is the active document
      if (!editor || event.document !== editor.document) {
        return;
      }

      // Only analyze certain file types
      const language = event.document.languageId;
      const supportedLanguages = [
        "javascript",
        "typescript",
        "python",
        "java",
        "cpp",
        "c",
        "go",
        "rust",
      ];

      if (!supportedLanguages.includes(language)) {
        return;
      }

      // Clear existing timeout
      if (analysisTimeout) {
        clearTimeout(analysisTimeout);
      }

      // Set new timeout for analysis
      analysisTimeout = setTimeout(async () => {
        await analyzeDocumentInline(event.document);
      }, ANALYSIS_DELAY);
    }
  );

  // Listen for active editor changes
  const editorChangeListener = vscode.window.onDidChangeActiveTextEditor(
    (editor) => {
      if (editor && inlineAnalysisPanel) {
        // Trigger analysis for new file
        setTimeout(async () => {
          await analyzeDocumentInline(editor.document);
        }, 500);
      }
    }
  );

  // Register all commands and listeners
  context.subscriptions.push(
    analyzeFileCommand,
    analyzePRCommand,
    dashboardCommand,
    toggleInlineCommand,
    documentChangeListener,
    editorChangeListener
  );

  // Auto-start inline analysis panel
  createInlineAnalysisPanel();
}

async function analyzeCode(code: string, fileName: string): Promise<string> {
  // This will call your PullSense API
  const response = await fetch(`${PULLSENSE_API_URL}/analyze-code`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      code: code,
      fileName: fileName,
      language: getLanguageFromFileName(fileName),
    }),
  });

  if (!response.ok) {
    throw new Error(`API call failed: ${response.statusText}`);
  }

  const result: any = await response.json(); // Add type annotation
  return result.analysis || "No analysis available";
}

// New function for inline document analysis
async function analyzeDocumentInline(document: vscode.TextDocument) {
  if (!inlineAnalysisPanel) {
    return;
  }

  const fileName = document.fileName;
  const fileContent = document.getText();

  // Skip if file is too large (> 10KB)
  if (fileContent.length > 50000) {
    updateInlineAnalysisPanel(
      "File too large for real-time analysis",
      fileName
    );
    return;
  }

  // Skip if file is empty or too small
  if (fileContent.trim().length < 10) {
    updateInlineAnalysisPanel(
      "Write some code to get suggestions...",
      fileName
    );
    return;
  }

  try {
    updateInlineAnalysisPanel("🔍 Analyzing...", fileName);
    const analysis = await analyzeCodeQuick(fileContent, fileName);
    updateInlineAnalysisPanel(analysis, fileName);
  } catch (error) {
    updateInlineAnalysisPanel(`Error: ${error}`, fileName);
  }
}

// Quick analysis function for inline suggestions
async function analyzeCodeQuick(
  code: string,
  fileName: string
): Promise<string> {
  const response = await fetch(`${PULLSENSE_API_URL}/analyze-code`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      code: code,
      fileName: fileName,
      language: getLanguageFromFileName(fileName),
      mode: "quick", // Add mode for shorter analysis
    }),
  });

  if (!response.ok) {
    throw new Error(`API call failed: ${response.statusText}`);
  }

  const result: any = await response.json(); // Add type annotation
  return result.analysis || "No suggestions available";
}

// Create inline analysis panel
function createInlineAnalysisPanel() {
  if (inlineAnalysisPanel) {
    return;
  }

  inlineAnalysisPanel = vscode.window.createWebviewPanel(
    "pullsenseInline",
    "🧠 PullSense Live",
    vscode.ViewColumn.Two,
    {
      enableScripts: true,
      retainContextWhenHidden: true,
    }
  );

  inlineAnalysisPanel.webview.html = getInlineAnalysisHtml();

  // Handle panel disposal
  inlineAnalysisPanel.onDidDispose(() => {
    inlineAnalysisPanel = undefined;
  });

  // Trigger initial analysis if there's an active editor
  const editor = vscode.window.activeTextEditor;
  if (editor) {
    setTimeout(async () => {
      await analyzeDocumentInline(editor.document);
    }, 1000);
  }
}

// Update inline analysis panel content
function updateInlineAnalysisPanel(analysis: string, fileName: string) {
  if (!inlineAnalysisPanel) {
    return;
  }

  const shortFileName = fileName.split("/").pop() || fileName;

  inlineAnalysisPanel.webview.postMessage({
    type: "updateAnalysis",
    analysis: analysis,
    fileName: shortFileName,
    timestamp: new Date().toLocaleTimeString(),
  });
}

// Helper function to show analysis results
function showAnalysisResults(analysis: string, fileName: string) {
  const panel = vscode.window.createWebviewPanel(
    "pullsenseAnalysis",
    `Analysis: ${fileName}`,
    vscode.ViewColumn.Two,
    {
      enableScripts: true,
    }
  );

  panel.webview.html = getAnalysisHtml(analysis, fileName);
}

// Helper function to get language from file extension
function getLanguageFromFileName(fileName: string): string {
  const extension = fileName.split(".").pop()?.toLowerCase();
  const languageMap: { [key: string]: string } = {
    js: "javascript",
    ts: "typescript",
    py: "python",
    java: "java",
    cpp: "cpp",
    c: "c",
    go: "go",
    rs: "rust",
  };
  return languageMap[extension || ""] || "unknown";
}

// HTML for the dashboard webview
function getDashboardHtml(): string {
  return `
    <!DOCTYPE html>
    <html>
    <head>
        <title>PullSense Dashboard</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; }
            .header { color: #007ACC; border-bottom: 2px solid #007ACC; padding-bottom: 10px; }
            .section { margin: 20px 0; }
            .button { background: #007ACC; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🧠 PullSense Dashboard</h1>
        </div>
        <div class="section">
            <h2>Quick Actions</h2>
            <button class="button" onclick="window.open('http://localhost:3000')">Open Web Dashboard</button>
        </div>
        <div class="section">
            <h2>Recent Analysis</h2>
            <p>Your recent code analysis results will appear here.</p>
        </div>
    </body>
    </html>`;
}

// HTML for analysis results
function getAnalysisHtml(analysis: string, fileName: string): string {
  return `
    <!DOCTYPE html>
    <html>
    <head>
        <title>Analysis Results</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; line-height: 1.6; }
            .header { color: #007ACC; border-bottom: 2px solid #007ACC; padding-bottom: 10px; }
            .analysis { background: #f5f5f5; padding: 15px; border-radius: 4px; margin: 15px 0; }
            pre { background: #2d2d30; color: #cccccc; padding: 15px; border-radius: 4px; overflow-x: auto; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📝 Analysis Results</h1>
            <h2>${fileName}</h2>
        </div>
        <div class="analysis">
            <pre>${analysis}</pre>
        </div>
    </body>
    </html>`;
}

// HTML for inline analysis panel
function getInlineAnalysisHtml(): string {
  return `
    <!DOCTYPE html>
    <html>
    <head>
        <title>PullSense Live Analysis</title>
        <style>
            body { 
                font-family: 'Segoe UI', Arial, sans-serif; 
                margin: 10px; 
                line-height: 1.5;
                background: #1e1e1e;
                color: #cccccc;
            }
            .header { 
                color: #4FC3F7; 
                border-bottom: 2px solid #4FC3F7; 
                padding-bottom: 8px; 
                margin-bottom: 15px;
                font-size: 16px;
            }
            .analysis-content { 
                background: #2d2d30; 
                padding: 12px; 
                border-radius: 6px; 
                margin: 10px 0;
                border-left: 3px solid #4FC3F7;
                font-size: 13px;
                max-height: 400px;
                overflow-y: auto;
            }
            .timestamp {
                color: #808080;
                font-size: 11px;
                margin-bottom: 8px;
            }
            .loading {
                color: #4FC3F7;
                font-style: italic;
            }
            .suggestion {
                background: #264f78;
                padding: 8px;
                margin: 5px 0;
                border-radius: 4px;
                border-left: 3px solid #4FC3F7;
            }
            .warning {
                background: #5a3a00;
                border-left-color: #ffcc00;
            }
            .error {
                background: #5a1e1e;
                border-left-color: #f44747;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h3 id="title">🧠 PullSense Live Analysis</h3>
        </div>
        <div class="timestamp" id="timestamp">Ready for analysis...</div>
        <div class="analysis-content" id="content">
            <div class="loading">Start typing to get AI suggestions...</div>
        </div>

        <script>
            window.addEventListener('message', event => {
                const message = event.data;
                
                if (message.type === 'updateAnalysis') {
                    document.getElementById('title').textContent = '🧠 ' + message.fileName;
                    document.getElementById('timestamp').textContent = 'Last updated: ' + message.timestamp;
                    
                    const content = document.getElementById('content');
                    content.innerHTML = formatAnalysis(message.analysis);
                }
            });

            function formatAnalysis(analysis) {
                if (analysis.includes('🔍 Analyzing...')) {
                    return '<div class="loading">' + analysis + '</div>';
                }
                
                if (analysis.includes('Error:')) {
                    return '<div class="error">' + analysis + '</div>';
                }
                
                // Simple formatting for suggestions
                let formatted = analysis
                    .replace(/\\n/g, '<br>')
                    .replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>')
                    .replace(/- (.*?)(<br>|$)/g, '<div class="suggestion">• $1</div>');
                
                return formatted || '<div class="loading">No suggestions yet...</div>';
            }
        </script>
    </body>
    </html>`;
}

export function deactivate() {
  if (analysisTimeout) {
    clearTimeout(analysisTimeout);
  }
  if (inlineAnalysisPanel) {
    inlineAnalysisPanel.dispose();
  }
}
