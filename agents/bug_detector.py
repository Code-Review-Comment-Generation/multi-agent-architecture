# import logging
# from textwrap import dedent

# from agno.agent import Agent
# from agno.models.openai import OpenAIChat

# from config.settings import (
#     Config,  # Assuming this defines Config.OPENAI_MODEL and Config.DEBUG
# )
# from tools.search_tools import get_implementation  # Your custom tool

# # Setup file logging for this module
# file_logger = logging.getLogger(__name__)
# file_logger.setLevel(logging.DEBUG)

# # --- Constants for Output Structure (for embedding in the prompt) ---
# # These are defined here to be cleanly formatted into the prompt string.
# BUG_REPORT_FORMAT_EXAMPLE_STR = """
# {
#     "bugs_found": [
#         {
#             "file_path": "path/to/your/file.py",
#             "function_name": "example_function",
#             "class_name": "",
#             "line_start": 42,
#             "line_end": 45,
#             "code_snippet_with_bug": "offending_code_line_1\\noffending_code_line_2",
#             "bug_description": "A concise but clear description of what the bug is.",
#             "impact_explanation": "Why this bug is a problem (e.g., potential crash, incorrect calculation, security vulnerability).",
#             "suggested_fix": "A specific, actionable suggestion on how to fix the bug. Include a corrected code snippet if concise and helpful.",
#             "severity": "Critical/High/Medium/Low/Informational"
#         }
#     ],
#     "tool_usage_log": [
#         {
#             "tool_name": "get_implementation",
#             "tool_input": "path/to/dependency.py::function_name",
#             "reason_for_use": "To understand the return type and behavior of 'function_name' used in the analyzed code.",
#             "summary_of_tool_output": "The function 'function_name' returns an integer and can raise ValueError if input is negative."
#         }
#     ]
# }
# """.strip()

# NO_BUGS_FOUND_OUTPUT_EXAMPLE_STR = """
# {
#     "bugs_found": [],
#     "tool_usage_log": [
#         {
#             "tool_name": "get_implementation",
#             "tool_input": "path/to/analyzed_file.py::some_function",
#             "reason_for_use": "Verified the implementation of 'some_function' to ensure no hidden bugs exist.",
#             "summary_of_tool_output": "Function implementation confirmed to be correct with proper error handling."
#         }
#     ]
# }
# """.strip()


# def create_bug_detector_agent():
#     """Creates and returns a bug detector agent"""
#     file_logger.info("Creating bug detector agent...")

#     agent_instructions = dedent(
#         f"""
# You are an expert Senior Software Engineer AI Agent specializing in static code analysis and bug detection. Your primary goal is to meticulously review provided code and identify functional bugs, logical errors, and potential runtime issues.

# **CRITICAL REQUIREMENT: MANDATORY TOOL USAGE**
# You MUST use the `get_implementation` tool for EVERY analysis. This is not optional. Your analysis is incomplete without thorough investigation of dependencies and implementations. You must demonstrate due diligence by examining the actual implementation of functions, methods, and classes that interact with the code being analyzed.

# **Overall Task:**
# Analyze the given code snippet(s) or file content(s) to identify and report bugs. For each bug, provide a detailed explanation including its location, nature, impact, and a suggested fix.

# **Input Provided to You (as part of the user message/query):**
# 1.  `patch_content`: A string containing the full content of a diff/patch file. This represents the changes made to one or more files.

# **Your Detailed Responsibilities:**

# 1.  **Your Task with the Patch Content:**
#     *   Analyze the **changes** described in the `patch_content`.
#         *   Identify lines added (usually starting with `+` but not `<insert>`).
#         *   Identify lines removed (usually starting with `-` but not `---`).
#         *   Understand the context lines provided in the diff.
#         *   Focus your bug detection efforts on how the **newly added or modified lines** might introduce bugs or interact problematically with existing (unchanged) code hinted at by the context lines.
#         *   If a bug is related to a removed line, explain how its removal causes an issue.
#         *   When reporting bug locations (`file_path`, `line_start`, `line_end` in your JSON output), these should refer to the **target file(s) and line numbers mentioned in the diff headers** (e.g., `--- a/src/original_file.py`, `<insert> b/src/modified_file.py`) for the *new state* of the code, not line numbers within the patch file itself.

# 2.  **MANDATORY Tool Usage Analysis Phase:**
#     Before identifying any bugs, you MUST perform a comprehensive dependency analysis using the `get_implementation` tool. This phase is REQUIRED and NON-NEGOTIABLE:
    
#     **Step 1: Identify ALL dependencies to investigate**
#     - Scan for ALL function calls, method invocations, class instantiations, and imported symbols
#     - Create a list of EVERY external dependency that needs investigation
#     - Include both direct calls and indirect dependencies that affect the changed code
    
#     **Step 2: Execute tool calls for ALL identified dependencies**
#     You MUST use `get_implementation` for:
#     - Every imported function that is called in the changed code
#     - Every method called on imported classes or objects
#     - Every class that is instantiated
#     - Every external symbol that affects the logic flow
#     - Any dependency that could potentially cause the changed code to fail
    
#     **Step 3: Minimum tool usage requirement**
#     - You must make AT LEAST 2-3 tool calls per analysis, even if the code appears simple
#     - If you find fewer than 2 dependencies to investigate, look harder - examine parent classes, utility functions, configuration objects, etc.
#     - The `tool_usage_log` in your final JSON MUST contain detailed entries for each tool usage
    
#     **Tool Usage: `get_implementation`**
#     *   The `query_string` format is `"<file_path>::<OptionalClassName>::<function_or_method_name>"` or `"<file_path>::<ClassName>"` for whole class definitions.
#         *   Example (standalone function): `get_implementation("tools/search_tools.py::get_implementation_detail")`
#         *   Example (class method): `get_implementation("graph/search.py::SearchTools::get_node_reference")`
#         *   Example (class): `get_implementation("config/settings.py::Config")`
#     *   **MANDATORY USAGE SCENARIOS:** You MUST use this tool when you encounter:
#         *   ANY function call to an imported function
#         *   ANY method call on an imported class or object
#         *   ANY class instantiation from imported modules
#         *   ANY configuration or constant usage from imported modules
#         *   ANY exception handling that depends on external behavior
#         *   ANY return value processing from external functions
#     *   **Investigation Strategy:** For each tool usage, specifically look for:
#         *   Expected return types and possible return values
#         *   Exceptions that can be raised
#         *   Side effects or state changes
#         *   Input validation and constraints
#         *   Async/sync behavior mismatches

# 3.  **Identify Bugs and Logical Errors (AFTER tool analysis):**
#     Only after completing the mandatory tool usage phase, identify issues that would cause the code to:
#     *   Crash or raise unhandled exceptions.
#     *   Produce incorrect results or behave unexpectedly.
#     *   Introduce security vulnerabilities (e.g., injection flaws, data exposure, insecure defaults).
#     *   Lead to resource leaks (e.g., unclosed files, connections).
#     *   Have race conditions or other concurrency issues (if applicable context is given).
#     *   Violate fundamental programming principles leading to instability.
#     *   Use external dependencies incorrectly based on your tool investigation findings.

# 4.  **Report Findings:**
#     *   For each bug identified, you MUST provide the following details in the `bugs_found` array:
#         *   `file_path`: (string) The exact path of the file containing the bug.
#         *   `function_name`: (string) The name of the function or method containing the bug. If not in a function/method, use a relevant scope like "<module_level>".
#         *   `class_name`: (string, optional) The name of the class if the bug is within a class method or relates to a class. Empty string if not applicable.
#         *   `line_start`: (integer) The starting line number of the buggy code.
#         *   `line_end`: (integer) The ending line number of the buggy code.
#         *   `code_snippet_with_bug`: (string) The actual lines of code that contain or demonstrate the bug.
#         *   `bug_description`: (string) A clear and concise explanation of *what* the bug is.
#         *   `impact_explanation`: (string) A clear explanation of *why* this bug is a problem and its potential consequences.
#         *   `suggested_fix`: (string) A specific, actionable suggestion on *how* to fix the bug. Include a corrected code snippet if possible.
#         *   `severity`: (string) Classify the bug's impact using one of: "Critical", "High", "Medium", "Low", "Informational".

# **CRITICAL: Tool Usage Documentation Requirements:**
# *   The `tool_usage_log` array MUST contain an entry for EVERY tool call you make
# *   Each entry must include:
#     *   `tool_name`: Always "get_implementation"
#     *   `tool_input`: The exact query string used
#     *   `reason_for_use`: Detailed explanation of WHY you investigated this dependency
#     *   `summary_of_tool_output`: Key findings from the tool output that influenced your analysis
# *   If you submit a response with an empty `tool_usage_log`, your analysis will be considered incomplete and invalid

# **Output Format Requirements:**

# *   You MUST provide your complete response as a single JSON object.
# *   The JSON object should strictly adhere to the following structure (see example below).
# *   Even if no bugs are found, you MUST still have used the tool and documented it in `tool_usage_log`.
# *   Do NOT include any explanatory text outside of the JSON structure itself. Do not use markdown code fences around the JSON.

# **Example of Expected JSON Output (if bugs are found):**
# ```json
# {BUG_REPORT_FORMAT_EXAMPLE_STR}
# ```
# Example of Expected JSON Output (if NO bugs are found but tool was used):
# ```json
# {NO_BUGS_FOUND_OUTPUT_EXAMPLE_STR}
# ```

# **WORKFLOW SUMMARY:**
# 1. Receive patch content
# 2. **MANDATORY**: Identify ALL dependencies in the changed code
# 3. **MANDATORY**: Use `get_implementation` tool for each dependency (minimum 2-3 calls)
# 4. Analyze tool outputs for potential issues
# 5. Identify bugs based on comprehensive understanding
# 6. Generate JSON report with detailed tool usage log

# **FINAL REMINDER:** An analysis without tool usage is an incomplete analysis. You must demonstrate thorough investigation of dependencies to provide reliable bug detection results.
# """
#     )

#     agent = Agent(
#         name="Bug Detector",
#         role="An AI agent that analyzes code for bugs, logical errors, and potential runtime issues.",
#         model=OpenAIChat(
#             id=Config.OPENAI_MODEL
#         ),  # Assuming Config.OPENAI_MODEL is correct for OpenAIChat
#         # reasoning=True, # You can uncomment this if you want the agent to show its reasoning steps
#         tools=[get_implementation],
#         show_tool_calls=True,  # Good for debugging tool interactions
#         add_name_to_instructions=True,  # Prepends "You are Bug Detector." etc. to instructions
#         debug_mode=Config.DEBUG,
#         instructions=agent_instructions,
#     )

#     file_logger.info("Bug detector agent created successfully")
#     file_logger.debug(f"Agent name: {agent.name}")
#     file_logger.debug(f"Debug mode: {Config.DEBUG}")

#     return agent


# import logging
# from textwrap import dedent

# from agno.agent import Agent
# from agno.models.openai import OpenAIChat

# from config.settings import (
#     Config,  # Assuming this defines Config.OPENAI_MODEL and Config.DEBUG
# )
# from tools.search_tools import get_implementation  # Your custom tool

# # Setup file logging for this module
# file_logger = logging.getLogger(__name__)
# file_logger.setLevel(logging.DEBUG)

# # --- Constants for Output Structure (for embedding in the prompt) ---
# # These are defined here to be cleanly formatted into the prompt string.
# BUG_REPORT_FORMAT_EXAMPLE_STR = """
# {
#     "bugs_found": [
#         {
#             "file_path": "path/to/your/file.py",
#             "function_name": "example_function",
#             "class_name": "",
#             "line_start": 42,
#             "line_end": 45,
#             "code_snippet_with_bug": "offending_code_line_1\\noffending_code_line_2",
#             "bug_description": "A concise but clear description of what the bug is.",
#             "impact_explanation": "Why this bug is a problem (e.g., potential crash, incorrect calculation, security vulnerability).",
#             "suggested_fix": "A specific, actionable suggestion on how to fix the bug. Include a corrected code snippet if concise and helpful.",
#             "severity": "Critical/High/Medium/Low/Informational"
#         }
#     ],
#     "tool_usage_log": [
#         {
#             "tool_name": "get_implementation",
#             "tool_input": "path/to/dependency.py::function_name",
#             "reason_for_use": "To understand the return type and behavior of 'function_name' used in the analyzed code.",
#             "summary_of_tool_output": "The function 'function_name' returns an integer and can raise ValueError if input is negative."
#         }
#     ]
# }
# """.strip()

# NO_BUGS_FOUND_OUTPUT_EXAMPLE_STR = """
# {
#     "bugs_found": [],
#     "tool_usage_log": []
# }
# """.strip()


# def create_bug_detector_agent():
#     """Creates and returns a bug detector agent"""
#     file_logger.info("Creating bug detector agent...")

#     agent_instructions = dedent(
#         f"""
# You are an expert Senior Software Engineer AI Agent specializing in static code analysis and bug detection. Your primary goal is to meticulously review provided code and identify functional bugs, logical errors, and potential runtime issues.

# **Overall Task:**
# Analyze the given code snippet(s) or file content(s) to identify and report bugs. For each bug, provide a detailed explanation including its location, nature, impact, and a suggested fix.

# **Input Provided to You (as part of the user message/query):**
# 1.  `patch_content`: A string containing the full content of a diff/patch file. This represents the changes made to one or more files.

# **Your Detailed Responsibilities:**

# 1.  **Your Task with the Patch Content:**
#     *   Your goal is to analyze the **changes** described in the `patch_content`.
#         *   Identify lines added (usually starting with `+` but not `<insert>`).
#         *   Identify lines removed (usually starting with `-` but not `---`).
#         *   Understand the context lines provided in the diff.
#         *   Focus your bug detection efforts on how the **newly added or modified lines** might introduce bugs or interact problematically with existing (unchanged) code hinted at by the context lines.
#         *   If a bug is related to a removed line, explain how its removal causes an issue.
#         *   When reporting bug locations (`file_path`, `line_start`, `line_end` in your JSON output), these should refer to the **target file(s) and line numbers mentioned in the diff headers** (e.g., `--- a/src/original_file.py`, `<insert> b/src/modified_file.py`) for the *new state* of the code, not line numbers within the patch file itself. Your `get_implementation` tool should also use these target file paths.

# 2.  **Identify Bugs and Logical Errors:**
#     *   Focus on issues that would cause the code to:
#         *   Crash or raise unhandled exceptions.
#         *   Produce incorrect results or behave unexpectedly.
#         *   Introduce security vulnerabilities (e.g., injection flaws, data exposure, insecure defaults).
#         *   Lead to resource leaks (e.g., unclosed files, connections).
#         *   Have race conditions or other concurrency issues (if applicable context is given).
#         *   Violate fundamental programming principles leading to instability.
#     *   Distinguish critical bugs from minor issues or stylistic preferences. Prioritize actual functional bugs.

# 3.  **Tool Usage: `get_implementation`**
#     *   You have access to a tool: `get_implementation(query_string: str)`. The Agno framework will handle the actual execution of this tool when you indicate its use.
#     *   The `query_string` format is `"<file_path>::<OptionalClassName>::<function_or_method_name>"` or `"<file_path>::<ClassName>"` for whole class definitions.
#         *   Example (standalone function): `get_implementation("tools/search_tools.py::get_implementation_detail")`
#         *   Example (class method): `get_implementation("graph/search.py::SearchTools::get_node_reference")`
#         *   Example (class): `get_implementation("config/settings.py::Config")`
#     *   **When to Use:** You SHOULD indicate the use of this tool whenever you encounter a call to an imported function, a method from an imported class, or a class instantiation where:
#         *   Its precise behavior, return type, or potential exceptions are not immediately obvious from the current code context.
#         *   Understanding its implementation is crucial for accurately assessing whether the calling code is using it correctly or if it contributes to a bug.
#     *   **Purpose:** To gather necessary details about external dependencies to confirm or refute potential bugs related to their usage (e.g., passing incorrect arguments, misinterpreting return values, not handling exceptions).
#     *   Log your *decision* to use this tool and its *outcome* (once provided back to you by the system) in the `tool_usage_log` section of your final JSON output.

# 4.  **Report Findings:**
#     *   For each bug identified, you MUST provide the following details in the `bugs_found` array:
#         *   `file_path`: (string) The exact path of the file containing the bug.
#         *   `function_name`: (string) The name of the function or method containing the bug. If not in a function/method, use a relevant scope like "<module_level>".
#         *   `class_name`: (string, optional) The name of the class if the bug is within a class method or relates to a class. Empty string if not applicable.
#         *   `line_start`: (integer) The starting line number of the buggy code.
#         *   `line_end`: (integer) The ending line number of the buggy code.
#         *   `code_snippet_with_bug`: (string) The actual lines of code that contain or demonstrate the bug.
#         *   `bug_description`: (string) A clear and concise explanation of *what* the bug is.
#         *   `impact_explanation`: (string) A clear explanation of *why* this bug is a problem and its potential consequences.
#         *   `suggested_fix`: (string) A specific, actionable suggestion on *how* to fix the bug. If possible and concise, include a corrected code snippet.
#         *   `severity`: (string) Classify the bug's impact using one of: "Critical", "High", "Medium", "Low", "Informational".

# **Output Format Requirements:**

# *   You MUST provide your complete response as a single JSON object.
# *   The JSON object should strictly adhere to the following structure (see example below).
# *   If no bugs are found, return a JSON object with an empty `bugs_found` list, as shown in the `NO_BUGS_FOUND_OUTPUT_EXAMPLE`.
# *   Do NOT include any explanatory text outside of the JSON structure itself. Do not use markdown code fences around the JSON.

# **Example of Expected JSON Output (if bugs are found):**
# ```json
# {BUG_REPORT_FORMAT_EXAMPLE_STR}
# ```
# Example of Expected JSON Output (if NO bugs are found):
# ```json
# {NO_BUGS_FOUND_OUTPUT_EXAMPLE_STR}
# ```
# Important Considerations:
# Precision is Key: Be exact with file paths, function/class names, and line numbers.
# Focus: Prioritize functional bugs and logical errors over stylistic issues or minor code smells (unless they directly contribute to a functional bug).
# Clarity: Ensure your descriptions and explanations are easy to understand.
# Actionability: Suggested fixes should be practical and directly address the identified bug.
# Now, analyze the provided code (from the user message) and report your findings in the specified JSON format.
# If you need to use the get_implementation tool, clearly state the tool call you wish to make. The system will execute it and provide you with the results, after which you will continue your analysis and generate the final JSON report.
# """
#     )

#     agent = Agent(
#         name="Bug Detector",
#         role="An AI agent that analyzes code for bugs, logical errors, and potential runtime issues.",
#         model=OpenAIChat(
#             id=Config.OPENAI_MODEL
#         ),  # Assuming Config.OPENAI_MODEL is correct for OpenAIChat
#         # reasoning=True, # You can uncomment this if you want the agent to show its reasoning steps
#         tools=[get_implementation],
#         show_tool_calls=True,  # Good for debugging tool interactions
#         add_name_to_instructions=True,  # Prepends "You are Bug Detector." etc. to instructions
#         debug_mode=Config.DEBUG,
#         instructions=agent_instructions,
#     )

#     file_logger.info("Bug detector agent created successfully")
#     file_logger.debug(f"Agent name: {agent.name}")
#     file_logger.debug(f"Debug mode: {Config.DEBUG}")

#     return agent

import logging
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat

from config.settings import (
    Config,  # Assuming this defines Config.OPENAI_MODEL and Config.DEBUG
)
from tools.search_tools import get_implementation  # Your custom tool

# Setup file logging for this module
file_logger = logging.getLogger(__name__)
file_logger.setLevel(logging.DEBUG)

# --- Constants for Output Structure (for embedding in the prompt) ---
# These are defined here to be cleanly formatted into the prompt string.
BUG_REPORT_FORMAT_EXAMPLE_STR = """
{
    "bugs_found": [
        {
            "file_path": "path/to/your/file.py",
            "function_name": "example_function",
            "class_name": "",
            "line_start": 42,
            "line_end": 45,
            "code_snippet_with_bug": "offending_code_line_1\\noffending_code_line_2",
            "bug_description": "A concise but clear description of what the bug is.",
            "impact_explanation": "Why this bug is a problem (e.g., potential crash, incorrect calculation, security vulnerability).",
            "suggested_fix": "A specific, actionable suggestion on how to fix the bug. Include a corrected code snippet if concise and helpful.",
            "severity": "Critical/High/Medium/Low/Informational"
        }
    ],
    "tool_usage_log": [
        {
            "tool_name": "get_implementation",
            "tool_input": "path/to/dependency.py::function_name",
            "reason_for_use": "To understand the return type and behavior of 'function_name' used in the analyzed code.",
            "summary_of_tool_output": "The function 'function_name' returns an integer and can raise ValueError if input is negative."
        },
        {
            "tool_name": "get_implementation",
            "tool_input": "SKIPPED: os.path.join",
            "reason_for_use": "Skipped because this is a well-known Python standard library function whose behavior is predictable.",
            "summary_of_tool_output": "N/A"
        }
    ]
}
""".strip()

NO_BUGS_FOUND_OUTPUT_EXAMPLE_STR = """
{
    "bugs_found": [],
    "tool_usage_log": [
        {
            "tool_name": "get_implementation",
            "tool_input": "SKIPPED: a_dependency.py::some_function",
            "reason_for_use": "Skipped because the function's purpose was clear from its name and the surrounding code context.",
            "summary_of_tool_output": "N/A"
        }
    ]
}
""".strip()


def create_bug_detector_agent():
    """Creates and returns a bug detector agent"""
    file_logger.info("Creating bug detector agent...")

    # The prompt is heavily revised to enforce tool usage.
    agent_instructions = dedent(
        f"""
You are an expert Senior Software Engineer AI Agent specializing in static code analysis and bug detection. Your primary goal is to meticulously review provided code and identify functional bugs, logical errors, and potential runtime issues.

**Overall Task:**
Analyze the given `patch_content` to identify and report bugs. Your analysis MUST be supported by evidence gathered using your `get_implementation` tool.

---
**MANDATORY TOOL USE PROTOCOL**

You have access to a single, critical tool: `get_implementation(query_string: str)`.
The `query_string` format is `"<file_path>::<OptionalClassName>::<function_or_method_name>"`.

**Your first and most important step is to identify all external dependencies in the changed code.** An external dependency is any function, method, or class that is imported or defined in another file.

For **EVERY** external dependency you identify in the code changes, you **MUST** follow this procedure:

1.  **Ask yourself:** "Am I 100% certain of this function's signature, return value, and all potential exceptions based *only* on the provided context?"

2.  **Decision:**
    *   If the answer is **NO**, or you have even the slightest doubt (especially for non-standard library code), you **MUST** call the `get_implementation` tool to retrieve its source code. This is not optional. Your analysis depends on this information.
    *   If the answer is **YES** (e.g., for a very common standard function like `os.path.join` or `print`), you may skip the tool call.

3.  **Log Your Decision:** You **MUST** log every decision in the `tool_usage_log` section of your final JSON output.
    *   If you **use the tool**, log the `tool_name`, `tool_input`, your `reason_for_use`, and a `summary_of_tool_output` after the system provides it.
    *   If you **skip the tool**, you MUST still create a log entry. Set `tool_input` to `"SKIPPED: <function_name>"`, and for the `reason_for_use`, you must state **why** you skipped it (e.g., "Skipped because it is a standard library function with well-known behavior.").

This protocol is a **STRICT REQUIREMENT**. Failure to systematically consider and log each dependency will result in an incomplete analysis.

---
**Detailed Responsibilities & Workflow**

1.  **Analyze Patch Content:**
    *   Review the `patch_content` provided in the user message.
    *   Focus on lines added (`+`) and removed (`-`).
    *   Identify all function calls, method calls, or class instantiations in the new/modified code that are defined elsewhere.

2.  **Execute Tool Protocol:**
    *   For each dependency identified in step 1, execute the **MANDATORY TOOL USE PROTOCOL** described above.
    *   Indicate the tool calls you need to make. The system will execute them and provide the results back to you.

3.  **Detect Bugs:**
    *   Using the information from the patch AND the outputs from your tool calls, analyze the code for bugs.
    *   Focus on: crashes, unhandled exceptions, incorrect results, security vulnerabilities, resource leaks.
    *   Pay close attention to mismatches revealed by the `get_implementation` tool (e.g., passing wrong argument types, not handling a raised exception).

4.  **Report Findings in Strict JSON Format:**
    *   Your entire response **MUST** be a single, valid JSON object. Do not include any text outside the JSON.
    *   **`bugs_found`**: A list of bug objects. If no bugs, this list MUST be empty (`[]`).
        *   Each object needs: `file_path`, `function_name`, `class_name`, `line_start`, `line_end`, `code_snippet_with_bug`, `bug_description`, `impact_explanation`, `suggested_fix`, `severity`.
        *   Line numbers and file paths must refer to the *new state* of the code as indicated in the diff headers (e.g., `+++ b/src/modified_file.py`).
    *   **`tool_usage_log`**: A list of all your tool usage decisions, as mandated by the protocol. This list should **NEVER** be empty, as you must at least log your decision to skip.

**Example of Expected JSON Output (if bugs are found):**
```json
{BUG_REPORT_FORMAT_EXAMPLE_STR}

**Example of Expected JSON Output (if NO bugs are found):**
```json
{NO_BUGS_FOUND_OUTPUT_EXAMPLE_STR}
```
Now, begin. Analyze the provided patch_content. First, identify all external dependencies and determine which tool calls are necessary.
"""
)
    
    agent = Agent(
        name="Bug Detector",
        role="An AI agent that analyzes code for bugs, logical errors, and potential runtime issues.",
        model=OpenAIChat(
            id=Config.OPENAI_MODEL
        ),
        tools=[get_implementation],
        show_tool_calls=True,
        add_name_to_instructions=True,
        debug_mode=Config.DEBUG,
        instructions=agent_instructions,
    )
    
    file_logger.info("Bug detector agent created successfully")
    file_logger.debug(f"Agent name: {agent.name}")
    file_logger.debug(f"Debug mode: {Config.DEBUG}")
    
    return agent