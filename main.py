from agno.utils.pprint import pprint_run_response

from github_comment_generator import generate_github_comment
from workflows import TeamWorkflow

if __name__ == "__main__":
    print("=" * 80)
    print("GENERATING DETAILED ANALYSIS REPORT...")
    print("=" * 80)

    report = TeamWorkflow(
        # file_path="llm/default_plugins/openai_models.py",
        file_path="pr-19479.patch",
        debug_mode=False,
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
