from agno.utils.pprint import pprint_run_response

from workflows import TeamWorkflow

if __name__ == "__main__":
    # Run workflow
    # Set recreate_knowledge=True on first run or when URLs change
    report = TeamWorkflow(debug_mode=False, recreate_knowledge=True).run()
    # Print the report
    pprint_run_response(report, markdown=True, show_time=True)
