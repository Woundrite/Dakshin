import * as vscode from "vscode";
import { exec } from "child_process";
import * as path from "path";
import * as fs from "fs";

export function activate(context: vscode.ExtensionContext) {
    console.log("Dakshin Language Extension is now active!");

    // Register commands
    const compileCommand = vscode.commands.registerCommand(
        "dakshin.compile",
        () => {
            compileDakshinFile();
        }
    );

    const runCommand = vscode.commands.registerCommand("dakshin.run", () => {
        compileAndRun();
    });

    const createProjectCommand = vscode.commands.registerCommand(
        "dakshin.createProject",
        () => {
            createNewProject();
        }
    );

    const showASTCommand = vscode.commands.registerCommand(
        "dakshin.showAST",
        () => {
            showAST();
        }
    );

    // Register language features
    const completionProvider = vscode.languages.registerCompletionItemProvider(
        "dakshin",
        new DakshinCompletionProvider(),
        "."
    );

    const diagnosticCollection =
        vscode.languages.createDiagnosticCollection("dakshin");
    context.subscriptions.push(diagnosticCollection);

    // Auto-compile on save (if enabled)
    const onSaveHandler = vscode.workspace.onDidSaveTextDocument((document) => {
        if (document.languageId === "dakshin") {
            const config = vscode.workspace.getConfiguration("dakshin");
            if (config.get("build.autoSave")) {
                compileDakshinFile();
            }
            // Run diagnostics
            validateDakshinFile(document, diagnosticCollection);
        }
    });

    // Register providers and handlers
    context.subscriptions.push(
        compileCommand,
        runCommand,
        createProjectCommand,
        showASTCommand,
        completionProvider,
        onSaveHandler
    );

    // Initialize diagnostics for open files
    vscode.workspace.textDocuments.forEach((doc) => {
        if (doc.languageId === "dakshin") {
            validateDakshinFile(doc, diagnosticCollection);
        }
    });
}

class DakshinCompletionProvider implements vscode.CompletionItemProvider {
    provideCompletionItems(
        document: vscode.TextDocument,
        position: vscode.Position
    ): vscode.CompletionItem[] {
        const completions: vscode.CompletionItem[] = [];

        // Built-in functions
        const builtinFunctions = [
            "print",
            "println",
            "input",
            "length",
            "abs",
            "min",
            "max",
            "malloc",
            "free",
            "system",
            "time",
            "exit",
            "strlen",
            "strcmp",
            "strcpy",
            "strcat",
            "msgbox",
            "alert",
            "confirm",
            "beep",
        ];

        builtinFunctions.forEach((func) => {
            const completion = new vscode.CompletionItem(
                func,
                vscode.CompletionItemKind.Function
            );
            completion.detail = `Built-in function: ${func}`;
            completion.documentation = new vscode.MarkdownString(
                `Dakshin built-in function \`${func}\``
            );
            completions.push(completion);
        });

        // Keywords
        const keywords = [
            "function",
            "let",
            "var",
            "const",
            "if",
            "else",
            "while",
            "for",
            "break",
            "continue",
            "return",
            "true",
            "false",
            "null",
        ];

        keywords.forEach((keyword) => {
            const completion = new vscode.CompletionItem(
                keyword,
                vscode.CompletionItemKind.Keyword
            );
            completion.detail = `Keyword: ${keyword}`;
            completions.push(completion);
        });

        return completions;
    }
}

function compileDakshinFile() {
    const editor = vscode.window.activeTextEditor;
    if (!editor || editor.document.languageId !== "dakshin") {
        vscode.window.showErrorMessage("No Dakshin file is currently open");
        return;
    }

    const filePath = editor.document.uri.fsPath;
    const workspaceFolder = vscode.workspace.getWorkspaceFolder(
        editor.document.uri
    );
    const config = vscode.workspace.getConfiguration("dakshin");
    const compilerPath = config.get("compiler.path", "python src/compiler.py");

    if (!workspaceFolder) {
        vscode.window.showErrorMessage("No workspace folder found");
        return;
    }

    // Save the file first
    editor.document.save();

    const outputChannel = vscode.window.createOutputChannel("Dakshin Compiler");
    outputChannel.show();
    outputChannel.appendLine(`Compiling: ${filePath}`);

    const workingDir = workspaceFolder.uri.fsPath;
    const relativePath = path.relative(workingDir, filePath);
    const asmPath = filePath.replace(".dn", ".asm");

    exec(
        `${compilerPath} "${relativePath}" "${asmPath}"`,
        { cwd: workingDir },
        (error, stdout, stderr) => {
            if (error) {
                outputChannel.appendLine(
                    `Compilation failed: ${error.message}`
                );
                outputChannel.appendLine(stderr);
                vscode.window.showErrorMessage(
                    "Compilation failed. Check output for details."
                );
            } else {
                outputChannel.appendLine("Compilation successful!");
                outputChannel.appendLine(stdout);
                vscode.window.showInformationMessage(
                    "Dakshin file compiled successfully!"
                );
            }
        }
    );
}

function compileAndRun() {
    const editor = vscode.window.activeTextEditor;
    if (!editor || editor.document.languageId !== "dakshin") {
        vscode.window.showErrorMessage("No Dakshin file is currently open");
        return;
    }

    const filePath = editor.document.uri.fsPath;
    const workspaceFolder = vscode.workspace.getWorkspaceFolder(
        editor.document.uri
    );

    if (!workspaceFolder) {
        vscode.window.showErrorMessage("No workspace folder found");
        return;
    }

    // Save the file first
    editor.document.save();

    const outputChannel = vscode.window.createOutputChannel("Dakshin Run");
    outputChannel.show();
    outputChannel.appendLine(`Building and running: ${filePath}`);

    const workingDir = workspaceFolder.uri.fsPath;
    const relativePath = path.relative(workingDir, filePath);
    const baseName = path.basename(filePath, ".dn");

    // Use build.bat for compilation and execution
    exec(
        `build.bat "${relativePath}"`,
        { cwd: workingDir },
        (error, stdout, stderr) => {
            if (error) {
                outputChannel.appendLine(`Build failed: ${error.message}`);
                outputChannel.appendLine(stderr);
                vscode.window.showErrorMessage(
                    "Build failed. Check output for details."
                );
            } else {
                outputChannel.appendLine("Build successful! Running...");
                outputChannel.appendLine(stdout);

                // Run the executable
                exec(
                    `${baseName}.exe`,
                    { cwd: workingDir },
                    (runError, runStdout, runStderr) => {
                        if (runError) {
                            outputChannel.appendLine(
                                `Runtime error: ${runError.message}`
                            );
                            outputChannel.appendLine(runStderr);
                        } else {
                            outputChannel.appendLine("Program output:");
                            outputChannel.appendLine(runStdout);
                        }
                    }
                );
            }
        }
    );
}

function createNewProject() {
    vscode.window
        .showInputBox({
            prompt: "Enter project name",
            placeHolder: "my-dakshin-project",
        })
        .then((projectName) => {
            if (!projectName) return;

            vscode.window
                .showOpenDialog({
                    canSelectFolders: true,
                    canSelectFiles: false,
                    canSelectMany: false,
                    openLabel: "Select project location",
                })
                .then((folders) => {
                    if (!folders || folders.length === 0) return;

                    const projectPath = path.join(
                        folders[0].fsPath,
                        projectName
                    );

                    try {
                        // Create project directory
                        fs.mkdirSync(projectPath, { recursive: true });

                        // Create main.dn file
                        const mainContent = `function main() {
    println("Hello, Dakshin!");
    println("Welcome to your new project: ${projectName}");
    return 0;
}`;
                        fs.writeFileSync(
                            path.join(projectPath, "main.dn"),
                            mainContent
                        );

                        // Create README.md
                        const readmeContent = `# ${projectName}

A Dakshin programming language project.

## Building

\`\`\`bash
python src/compiler.py main.dn main.asm
nasm -f win64 main.asm -o main.obj
link main.obj -o main.exe
\`\`\`

## Running

\`\`\`bash
./main.exe
\`\`\`
`;
                        fs.writeFileSync(
                            path.join(projectPath, "README.md"),
                            readmeContent
                        );

                        // Open the project
                        vscode.commands.executeCommand(
                            "vscode.openFolder",
                            vscode.Uri.file(projectPath)
                        );

                        vscode.window.showInformationMessage(
                            `Dakshin project '${projectName}' created successfully!`
                        );
                    } catch (error) {
                        vscode.window.showErrorMessage(
                            `Failed to create project: ${error}`
                        );
                    }
                });
        });
}

function showAST() {
    const editor = vscode.window.activeTextEditor;
    if (!editor || editor.document.languageId !== "dakshin") {
        vscode.window.showErrorMessage("No Dakshin file is currently open");
        return;
    }

    const filePath = editor.document.uri.fsPath;
    const workspaceFolder = vscode.workspace.getWorkspaceFolder(
        editor.document.uri
    );
    const config = vscode.workspace.getConfiguration("dakshin");
    const compilerPath = config.get("compiler.path", "python src/main.py");

    if (!workspaceFolder) {
        vscode.window.showErrorMessage("No workspace folder found");
        return;
    }

    const workingDir = workspaceFolder.uri.fsPath;
    const relativePath = path.relative(workingDir, filePath);

    exec(
        `${compilerPath} "${relativePath}"`,
        { cwd: workingDir },
        (error, stdout, stderr) => {
            if (error) {
                vscode.window.showErrorMessage(
                    `Failed to generate AST: ${error.message}`
                );
            } else {
                // Create a new document to show the AST
                vscode.workspace
                    .openTextDocument({
                        content: stdout,
                        language: "json",
                    })
                    .then((doc) => {
                        vscode.window.showTextDocument(doc);
                    });
            }
        }
    );
}

function validateDakshinFile(
    document: vscode.TextDocument,
    diagnosticCollection: vscode.DiagnosticCollection
) {
    const config = vscode.workspace.getConfiguration("dakshin");
    if (!config.get("linting.enabled")) {
        return;
    }

    const diagnostics: vscode.Diagnostic[] = [];
    const text = document.getText();
    const lines = text.split("\n");

    // Basic syntax checking
    lines.forEach((line, lineIndex) => {
        // Check for missing semicolons (basic check)
        if (
            line.trim().length > 0 &&
            !line.trim().endsWith(";") &&
            !line.trim().endsWith("{") &&
            !line.trim().endsWith("}") &&
            !line.trim().startsWith("//") &&
            !line.trim().startsWith("/*") &&
            !line.trim().startsWith("*") &&
            !line.trim().startsWith("function") &&
            !line.trim().startsWith("if") &&
            !line.trim().startsWith("while") &&
            !line.trim().startsWith("for") &&
            !line.trim().startsWith("else")
        ) {
            const diagnostic = new vscode.Diagnostic(
                new vscode.Range(
                    lineIndex,
                    line.length,
                    lineIndex,
                    line.length
                ),
                "Missing semicolon",
                vscode.DiagnosticSeverity.Warning
            );
            diagnostics.push(diagnostic);
        }

        // Check for unmatched brackets
        const openBrackets = (line.match(/\{/g) || []).length;
        const closeBrackets = (line.match(/\}/g) || []).length;
        if (openBrackets !== closeBrackets) {
            // This is a simple check - a more sophisticated parser would be needed for real bracket matching
        }
    });

    diagnosticCollection.set(document.uri, diagnostics);
}

export function deactivate() {
    console.log("Dakshin Language Extension has been deactivated");
}
