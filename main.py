import logging
import sys
from datetime import datetime

from agno.utils.pprint import pprint_run_response

from github_comment_generator import generate_github_comment
from workflows import TeamWorkflow


class TeeLogger:
    """Custom logger that writes to both file and console"""

    def __init__(self, file_path):
        self.terminal = sys.stdout
        self.log_file = open(file_path, "w", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log_file.write(message)
        self.log_file.flush()

    def flush(self):
        self.terminal.flush()
        self.log_file.flush()

    def close(self):
        self.log_file.close()


def setup_logging():
    """Setup logging to capture all output to agent_logs.txt"""
    # Configure root logger
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("agent_logs.txt", mode="w", encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )

    # Configure agno logger specifically
    agno_logger = logging.getLogger("agno")
    agno_logger.setLevel(logging.DEBUG)

    # Also capture stdout to file
    tee = TeeLogger("agent_logs.txt")
    sys.stdout = tee
    sys.stderr = tee

    return tee


if __name__ == "__main__":
    # Setup logging to capture all output
    tee = setup_logging()

    try:
        print("=" * 80)
        print("GENERATING DETAILED ANALYSIS REPORT...")
        print(f"Timestamp: {datetime.now()}")
        print("=" * 80)

        report = TeamWorkflow(
            # file_path="llm/default_plugins/openai_models.py",
            file_path="pr-19479.patch",
            debug_mode=True,  # Enable debug mode to capture more logs
            recreate_knowledge=True,
        ).run()

        report_list = list(report)

        print("\nDETAILED ANALYSIS REPORT:")
        print("=" * 80)
        pprint_run_response(iter(report_list), markdown=True, show_time=True)

        print("\n" + "=" * 80)
        print("GITHUB REVIEW COMMENT:")
        print("=" * 80)

        github_comment = generate_github_comment(iter(report_list))
        print(github_comment)
        print("=" * 80)
        print(f"Logs saved to: agent_logs.txt")

    finally:
        # Restore stdout and close log file
        sys.stdout = tee.terminal
        sys.stderr = sys.__stderr__
        tee.close()
