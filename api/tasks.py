from crewai import Task
from crewai import Task, Agent
from textwrap import dedent


from job_manager import append_event
from models import PositionInfo, PositionInfoList
# from utils.logging import logger


class CompanyResearchTasks():

    def __init__(self, job_id):
        self.job_id = job_id

    def append_event_callback(self, task_output):
        # logger.info("Callback called: %s", task_output)
        append_event(self.job_id, task_output.exported_output)

    def manage_research(self, agent: Agent, companies: list[str], positions: list[str], tasks: list[Task]):
        return Task(
            description=dedent(f"""Based on the list of companies {companies} and the positions {positions},
                use the results from the Company Research Agent to research each position in each company.
                to put together a json object containing the URLs for 3 blog articles, the URLs and title 
                for 3 YouTube interviews for each position in each company.
                               
                """),
            agent=agent,
            expected_output=dedent(
                """A json object containing the URLs for 3 blog articles and the URLs and 
                    titles for 3 YouTube interviews for each position in each company."""),
            callback=self.append_event_callback,
            context=tasks,
            output_json=PositionInfoList
        )

    def company_research(self, agent: Agent, company: str, positions: list[str]):
        return Task(
            description=dedent(f"""Research the position {positions} for the {company} company. 
                For each position, find the URLs for 3 recent blog articles and the URLs and titles for
                3 recent YouTube interviews for the person in each position.
                Return this collected information in a JSON object.
                               
                Helpful Tips:
                - To find the blog articles names and URLs, perform searches on Google such like the following:
                    - "{company} [POSITION HERE] blog articles"
                - To find the youtube interviews, perform searches on YouTube such as the following:
                    - "{company} [POSITION HERE] interview"
                               
                Important:
                - Once you've found the information, immediately stop searching for additional information.
                - Only return the requested information. NOTHING ELSE!
                - Do not generate fake information. Only return the information you find. Nothing else!
                - Do not stop researching until you find the requested information for each position in the company.
                """),
            agent=agent,
            expected_output="""A JSON object containing the researched information for each position in the company.""",
            callback=self.append_event_callback,
            output_json=PositionInfo,
            async_execution=True
        )


class PersonalizeEmailTask():
    def __init__(self, job_id):
        self.job_id = job_id

    def append_event_callback(self, task_output):
        # logger.info("Callback called: %s", task_output)
        append_event(self.job_id, task_output.exported_output)

    def personalize_email(self, agent, pdf_content, jd, email_template):
        return Task(
            description=f"""
                Personalize the template email for recipient using their information.

                - resume: {pdf_content}
                - job description: {jd}

                Important Info to consider:
                - When personalizing the email, first of all congratulate the 
                candidate for passing the first round of shortlisting candidates. Highlight important skills/experience which is relevant to the job.
                    And make sure to incorporate it naturally into the email.  without going too much in to detail.
                - Make sure to keep the updated email roughly the same same length as the template email.
                - Make sure you select the job title, the name of the comapny, name of the candidate and other necessary details from the {jd}
                The template email is as follows:

                ```
                {email_template}
                ```
            """,
            agent=agent,
            expected_output=f"Personalized email draft.",
            async_execution=True,
        )

    def ghostwrite_email(self, agent, draft_email):
        return Task(
            description=f"""
                Revise the draft email to adopt the following writing style.

                Writing Style:
                - Use a more formal, engaging, and slightly happy tone, mirroring ghost writer's final email communication style. 
                - This approach prioritizes clear, direct communication while maintaining a friendly and approachable tone. 
                - Use straightforward language, including phrases like "Hey [Name]!" to start emails or messages and end with "Regards". 
                - The tone will be optimistic and encouraging, aiming to build rapport and motivate action, while staying grounded in practical advice.

                Important Notes:
                - Do not use emojis.
            """,
            agent=agent,
            context=[draft_email],
            expected_output=f"A revised email draft in ghost writer's specified tone and style.",

        )


class HRTask():
    def __init__(self, job_id):
        self.job_id = job_id

    def append_event_callback(self, task_output):
        # logger.info("Callback called: %s", task_output)
        append_event(self.job_id, task_output.exported_output)

    def scoreHR(self, agent, pdf_content, jd):
        return Task(
            description=f"""
                provide a score indicating the suitability of the candidate for the specified role.


                - resume: {pdf_content}
                - job description: {jd}

                Important Info to consider:
                - Make sure you compare and contrast the skills required in {jd} and the skills present in {pdf_content}
                - Make sure you compare and contrast the experience required in {jd} and the skills present in {pdf_content}
                - After carefull accessment of both the things, then you give a score for the CV (from 1 to 10)
            """,
            agent=agent,
            expected_output=f"the score indicating the suitability of the candidate for the specified role",
            async_execution=True,
        )

    def explainHR(self, agent, score):
        return Task(
            description=f"""
                provide an explaination indicating the suitability of the candidate for the specified role.

                Important Info to consider:
                - Make sure you compare and contrast the skills required in job description and the skills present in resume.
                - Make sure you compare and contrast the experience required in job description and the skills present in resume.
                - After carefull accessment of both the things, then you give an explanation of the {score}
                - the explaination should be 2-4 sentences long. Not more than 4 sentences.

            """,
            agent=agent,
            expected_output=f"an explaination indicating the suitability of the candidate for the specified role",
            context=[score],
        )

    # def ghostwrite_explainHR(self, agent, explaination):
    #     return Task(
    #         description=f"""
    #             Revise the explaination to adopt the following writing style.

    #             Writing Style:
    #             - Use a more formal, engaging, and slightly honest tone, mirroring ghost writer's final email communication style.
    #             - This approach prioritizes clear, direct communication while maintaining a friendly and approachable tone.
    #             - Use straightforward language.
    #             - The tone will be optimistic and encouraging, aiming to build rapport and motivate action, while staying grounded in the honest review of the CV.

    #             Important Notes:
    #             - Do not use emojis.
    #         """,
    #         agent=agent,
    #         context=[explaination],
    #         expected_output=f"A revised explaination in ghost writer's specified tone and style.",

    #     )
