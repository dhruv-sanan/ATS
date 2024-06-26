from typing import List
from crewai import Agent
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from crewai_tools import SerperDevTool
from tools.youtube_search_tools import YoutubeVideoSearchTool

import os


class CompanyResearchAgents():

    def __init__(self):
        self.searchInternetTool = SerperDevTool()
        self.youtubeSearchTool = YoutubeVideoSearchTool()
        self.llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model="mixtral-8x7b-32768"
        )

    def research_manager(self, companies: List[str], positions: List[str]) -> Agent:
        return Agent(
            role="Company Research Manager",
            goal=f"""Generate a list of JSON objects containing the urls for 3 recent blog articles and 
                the url and title for 3 recent YouTube interview, for each position in each company.
             
                Companies: {companies}
                Positions: {positions}

                Important:
                - The final list of JSON objects must include all companies and positions. Do not leave any out.
                - If you can't find information for a specific position, fill in the information with the word "MISSING".
                - Do not generate fake information. Only return the information you find. Nothing else!
                - Do not stop researching until you find the requested information for each position in each company.
                - All the companies and positions exist so keep researching until you find the information for each one.
                - Make sure you each researched position for each company contains 3 blog articles and 3 YouTube interviews.
                """,
            backstory="""As a Company Research Manager, you are responsible for aggregating all the researched information
                into a list.""",
            llm=self.llm,
            tools=[self.searchInternetTool, self.youtubeSearchTool],
            verbose=True,
            allow_delegation=True
        )

    def company_research_agent(self) -> Agent:
        return Agent(
            role="Company Research Agent",
            goal="""Look up the specific positions for a given company and find urls for 3 recent blog articles and 
                the url and title for 3 recent YouTube interview for each person in the specified positions. It is your job to return this collected 
                information in a JSON object""",
            backstory="""As a Company Research Agent, you are responsible for looking up specific positions 
                within a company and gathering relevant information.
                
                Important:
                - Once you've found the information, immediately stop searching for additional information.
                - Only return the requested information. NOTHING ELSE!
                - Make sure you find the persons name who holds the position.
                - Do not generate fake information. Only return the information you find. Nothing else!
                """,
            tools=[self.searchInternetTool, self.youtubeSearchTool],
            llm=self.llm,
            verbose=True
        )


class EmailPersonalizationAgents():
    def __init__(self):
        self.llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model="mixtral-8x7b-32768"
        )

        # self.llm = ChatOpenAI(
        #     model="gpt-3.5-turbo",
        #     api_key=os.getenv("OPENAI_API_KEY")
        # )

    def personalize_email_agent(self):
        return Agent(
            role="Email Personalizer",
            goal=f"""
                Personalize template emails for candidates that have been selected for the interview stage.

                Given a template email and recipient information (name, email, resume), 
                personalize the email by incorporating the recipient's details 
                into the email while maintaining the core message and structure of the original email. 
                This involves updating the introduction, body, and closing of the email to make 
                it more personal and engaging for each recipient. Make sure to congratulate the 
                candidate for passing the first round of shortlisting candidates.
                """,
            backstory="""
                As an Email Personalizer, you are responsible for customizing template emails for individual recipients based on their information.
                """,
            verbose=True,
            llm=self.llm,
            max_iter=2,
        )

    def ghostwriter_agent(self):
        return Agent(
            role="Ghostwriter",
            goal=f"""
                Revise draft emails to adopt the Ghostwriter's writing style.

                Use an formal, engaging, and slightly corporate tone, mirroring the Ghostwriter's final email communication style.
                """,
            backstory="""
                As a Ghostwriter, you are responsible for revising draft emails to match the Ghostwriter's writing style, focusing on clear, direct communication with a formal, approachable and slightly happy tone.
                """,
            verbose=True,
            llm=self.llm,
            max_iter=2,
        )


class HRAgents():

    def __init__(self):
        self.llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model="mixtral-8x7b-32768"
        )
        # self.llm = ChatOpenAI(
        #     model="gpt-3.5-turbo",
        #     api_key=os.getenv("OPENAI_API_KEY")
        # )

    def scoreHR_agent(self) -> Agent:
        return Agent(
            role="Human Resource Manager",
            goal=f"""provide a score indicating the suitability of the candidate for the specified role

                Important:
                - The final result must include the score that you have decided to give. Do not give anything else than the score.
                - You have give a score for the CV (from 1 to 10). Do not give less than 1 and more than 10.
                - Do not generate fake scroe. 
                - Return the appropriate score which genuinely matches the resume with job description.
                - Make sure your score should reflect how much suitable is the candidate for the job.
                """,
            backstory="""As a Human Resource Manager, you are responsible for giving a score to the resume according to the job description of the role required in the company.""",
            llm=self.llm,
            verbose=True,
            max_iter=2,
        )

    def explainHR_agent(self) -> Agent:
        return Agent(
            role="Human Resource Manager",
            goal="""provide an explaination indicating the suitability of the candidate for the specified role.""",
            backstory="""As a Human Resource Manager, you are responsible to explaination indicating the suitability of the candidate for the specified role required
                within the company and gathering relevant information.
 
                Important Info to consider:
                - Make sure you compare and contrast the skills required in job description and the skills present in resume
                - Make sure you compare and contrast the experience required in job description and the skills present in resume
                - After carefull accessment of both the things, then you give an explanation of the score
                - the explaination should be 2-4 sentences long. Not more than 4 
                """,
            llm=self.llm,
            verbose=True,
            max_iter=2,)

    # def ghostwrite_explainHR_agent(self):
    #     return Agent(
    #         role="Ghostwriter",
    #         goal=f"""
    #             Revise explainations to adopt the Ghostwriter's writing style.

    #             Use an formal, engaging, and slightly corporate tone, mirroring the Ghostwriter's final email communication style.
    #             """,
    #         backstory="""
    #             As a Ghostwriter, you are responsible for revising explainations to match the Ghostwriter's writing style,
    #             focusing on clear, direct communication with a formal, approachable and slightly honest tone.
    #             """,
    #         verbose=True,
    #         llm=self.llm,
    #         max_iter=2,
    #     )
