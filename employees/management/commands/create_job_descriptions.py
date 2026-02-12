from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from employees.models import Department, Designation
from employees.models_job import JobDescription
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Create job descriptions for all open positions'

    def handle(self, *args, **kwargs):
        # Get or create departments
        tech_dept, _ = Department.objects.get_or_create(
            name='Technology',
            defaults={'description': 'Technology and Engineering Department'}
        )
        
        marketing_dept, _ = Department.objects.get_or_create(
            name='Marketing',
            defaults={'description': 'Marketing and Digital Media Department'}
        )
        
        qa_dept, _ = Department.objects.get_or_create(
            name='Quality Assurance',
            defaults={'description': 'Quality Assurance and Testing Department'}
        )
        
        design_dept, _ = Department.objects.get_or_create(
            name='Design',
            defaults={'description': 'UI/UX Design Department'}
        )
        
        # Get or create designations
        designations = {}
        designation_list = [
            ('Mobile App Developer', tech_dept),
            ('SEO/SMO Executive', marketing_dept),
            ('ROR Developer', tech_dept),
            ('Python Developer', tech_dept),
            ('PHP Developer', tech_dept),
            ('MERN Developer', tech_dept),
            ('Shopify Developer', tech_dept),
            ('HTML Developer', tech_dept),
            ('AI/ML Developer', tech_dept),
            ('UI/UX Designer', design_dept),
            ('Quality Analyst', qa_dept),
        ]
        
        for name, dept in designation_list:
            try:
                # Try to get existing designation first
                designations[name] = Designation.objects.get(name=name)
            except Designation.DoesNotExist:
                # Create if doesn't exist
                designations[name] = Designation.objects.create(
                    name=name,
                    department=dept,
                    description=f'{name} position'
                )
        
        # Get admin user for posted_by
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.first()
        
        # Application deadline (45 days from now)
        deadline = date.today() + timedelta(days=45)
        
        self.stdout.write(self.style.SUCCESS('Creating job descriptions...'))
        
        # Job 1: Flutter + iOS Developer
        self.create_job_1(designations, tech_dept, admin_user, deadline)
        
        # Job 2: Flutter + Android Developer
        self.create_job_2(designations, tech_dept, admin_user, deadline)
        
        # Job 3: SMO/SEO Executive
        self.create_job_3(designations, marketing_dept, admin_user, deadline)
        
        # Job 4: ROR + Next.JS Developer
        self.create_job_4(designations, tech_dept, admin_user, deadline)
        
        # Job 5: Python Developer
        self.create_job_5(designations, tech_dept, admin_user, deadline)
        
        # Job 6: PHP Developer
        self.create_job_6(designations, tech_dept, admin_user, deadline)
        
        # Job 7: MERN Developer
        self.create_job_7(designations, tech_dept, admin_user, deadline)
        
        # Job 8: Jr. Shopify Developer
        self.create_job_8(designations, tech_dept, admin_user, deadline)
        
        # Job 9: Jr. HTML Developer
        self.create_job_9(designations, tech_dept, admin_user, deadline)
        
        # Job 10: AI/ML Developer
        self.create_job_10(designations, tech_dept, admin_user, deadline)
        
        # Job 11: UI/UX Designer
        self.create_job_11(designations, design_dept, admin_user, deadline)
        
        # Job 12: Sr. Quality Analyst
        self.create_job_12(designations, qa_dept, admin_user, deadline)
        
        # Job 13: React Native Developer
        self.create_job_13(designations, tech_dept, admin_user, deadline)
        
        self.stdout.write(self.style.SUCCESS('Successfully created all 13 job descriptions!'))

    def create_job_1(self, designations, dept, user, deadline):
        """Flutter + iOS Developer"""
        job, created = JobDescription.objects.get_or_create(
            title='Mobile App Developer - Flutter + iOS',
            designation=designations['Mobile App Developer'],
            defaults={
                'department': dept,
                'employment_type': 'full_time',
                'experience_level': 'mid_level',
                'location': 'Ahmedabad',
                'work_mode': 'office',
                'number_of_vacancies': 1,
                'application_deadline': deadline,
                'status': 'active',
                'posted_by': user,
                'job_description': '''We are seeking an experienced Mobile App Developer specializing in Flutter and iOS Native development to join our dynamic team in Ahmedabad. The ideal candidate will have strong expertise in cross-platform mobile application development with at least 3 years of hands-on experience.

This role requires proficiency in Flutter framework combined with native iOS development skills, along with a proven track record of delivering high-quality mobile applications across various domains.''',
                'responsibilities': '''• Design and build advanced mobile applications for iOS platform using Flutter and native iOS technologies
• Collaborate with cross-functional teams to define, design, and ship new features
• Work with external data sources and APIs for seamless integration
• Develop Flutter widgets for both iOS and Android platforms
• Implement native iOS features using Swift, SwiftUI, and UIKit
• Unit-test code for robustness, including edge cases, usability, and general reliability
• Work on bug fixing and improving application performance
• Continuously discover, evaluate, and implement new technologies to maximize development efficiency
• Maintain code quality, organization, and automation standards
• Participate in code reviews and provide constructive feedback to team members
• Ensure applications meet quality standards and are optimized for performance
• Publish and maintain applications on App Store and Play Store
• Integrate third-party libraries and APIs as per project requirements
• Contribute in all phases of the development lifecycle (planning, design, development, testing, deployment)''',
                'requirements': '''Educational Qualifications:
• Bachelor's Degree in Computer Science, Information Technology, or related field

Experience Requirements:
• Minimum 3+ years of experience working as a full-time Mobile App Developer
• Must have executed at least 7-8 projects in different domains
• Strong technical knowledge about mobile application and web development

Technical Skills:
• Must have hands-on experience with Flutter & iOS development
• In-depth knowledge of Swift & Dart languages
• Strong knowledge of Flutter widgets for iOS and Android platforms
• Deep understanding of iOS SDK and Swift programming
• Proven experience developing iOS applications using SwiftUI and UIKit
• Experience in building mobile applications utilizing web services (SOAP/REST/JSON/GSON)
• Knowledge of App Store and Play Store publishing & distribution processes
• Experience with third-party libraries and APIs integration
• Good knowledge of databases (MySQL, SQLite, Realm)

Soft Skills:
• Exceptional analytical and problem-solving abilities
• Excellent interpersonal skills
• Great understanding of client requirements
• Pleasant and professional communication
• Very good interdepartmental coordination
• Innovative and out-of-the-box thinking
• Ability to work independently and in teams
• Strong attention to detail''',
                'experience_criteria': '''• Minimum 3 years of professional experience in mobile app development with Flutter and iOS
• Must have successfully delivered at least 7-8 mobile applications across different domains
• Proven track record of publishing apps on App Store and Play Store
• Experience working in Agile/Scrum development environments
• Hands-on experience with version control systems (Git)
• Experience with RESTful API integration and third-party services
• Strong portfolio demonstrating Flutter and iOS native app development capabilities''',
                'min_salary': 400000,
                'max_salary': 800000,
                'currency': 'INR',
                'travel_required': False,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created: {job.title}'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠ Already exists: {job.title}'))

    def create_job_2(self, designations, dept, user, deadline):
        """Flutter + Android Developer"""
        job, created = JobDescription.objects.get_or_create(
            title='Mobile App Developer - Flutter + Android',
            designation=designations['Mobile App Developer'],
            defaults={
                'department': dept,
                'employment_type': 'full_time',
                'experience_level': 'mid_level',
                'location': 'Ahmedabad',
                'work_mode': 'office',
                'number_of_vacancies': 1,
                'application_deadline': deadline,
                'status': 'active',
                'posted_by': user,
                'job_description': '''We are seeking an experienced Mobile App Developer specializing in Flutter and Android Native development to join our dynamic team in Ahmedabad. The ideal candidate will have strong expertise in cross-platform mobile application development with at least 3 years of hands-on experience.

This role requires proficiency in Flutter framework combined with native Android development skills, along with a proven track record of delivering high-quality mobile applications across various domains.''',
                'responsibilities': '''• Design and build advanced mobile applications for Android platform using Flutter and native Android technologies
• Collaborate with cross-functional teams to define, design, and ship new features
• Work with external data sources and APIs for seamless integration
• Develop Flutter widgets for both iOS and Android platforms
• Implement native Android features using Java, Kotlin, and Jetpack Compose
• Unit-test code for robustness, including edge cases, usability, and general reliability
• Work on bug fixing and improving application performance
• Continuously discover, evaluate, and implement new technologies to maximize development efficiency
• Maintain code quality, organization, and automation standards
• Participate in code reviews and provide constructive feedback to team members
• Ensure applications meet quality standards and are optimized for performance
• Publish and maintain applications on Play Store
• Integrate third-party libraries and APIs as per project requirements
• Contribute in all phases of the development lifecycle (planning, design, development, testing, deployment)''',
                'requirements': '''Educational Qualifications:
• Bachelor's Degree in Computer Science, Information Technology, or related field

Experience Requirements:
• Minimum 3+ years of experience working as a full-time Mobile App Developer
• Must have executed at least 7-8 projects in different domains
• Strong technical knowledge about mobile application and web development

Technical Skills:
• Must have hands-on experience with Flutter & Android development
• In-depth knowledge of Core Java, Kotlin & Dart languages
• Strong knowledge of Flutter widgets for iOS and Android platforms
• Expertise in Jetpack Compose for modern Android UI development
• Experience in building mobile applications utilizing web services (SOAP/REST/JSON/GSON)
• Knowledge of Play Store publishing & distribution processes
• Experience with third-party libraries and APIs integration
• Good knowledge of databases (MySQL, SQLite, Realm)

Soft Skills:
• Exceptional analytical and problem-solving abilities
• Excellent interpersonal skills
• Great understanding of client requirements
• Pleasant and professional communication
• Very good interdepartmental coordination
• Innovative and out-of-the-box thinking
• Ability to work independently and in teams
• Strong attention to detail''',
                'experience_criteria': '''• Minimum 3 years of professional experience in mobile app development with Flutter and Android
• Must have successfully delivered at least 7-8 mobile applications across different domains
• Proven track record of publishing apps on Play Store
• Experience working in Agile/Scrum development environments
• Hands-on experience with version control systems (Git)
• Experience with RESTful API integration and third-party services
• Strong portfolio demonstrating Flutter and Android native app development capabilities''',
                'min_salary': 400000,
                'max_salary': 800000,
                'currency': 'INR',
                'travel_required': False,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created: {job.title}'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠ Already exists: {job.title}'))

    def create_job_3(self, designations, dept, user, deadline):
        """SMO/SEO Executive"""
        job, created = JobDescription.objects.get_or_create(
            title='SMO/SEO Executive',
            designation=designations['SEO/SMO Executive'],
            defaults={
                'department': dept,
                'employment_type': 'full_time',
                'experience_level': 'junior',
                'location': 'Ahmedabad',
                'work_mode': 'office',
                'number_of_vacancies': 1,
                'application_deadline': deadline,
                'status': 'active',
                'posted_by': user,
                'job_description': '''We are looking for an experienced SMO/SEO Executive to join our marketing team in Ahmedabad. The ideal candidate will have at least 2 years of experience in search engine optimization and social media optimization, with a proven track record of improving website rankings and social media presence.''',
                'responsibilities': '''• Implementation of strategy pre-defined for On-Page/Off-Page site analysis and optimization
• Using various advanced tools for SEO research & analysis
• Perform ongoing keyword-meta titles analysis, discovery, expansion and optimization
• Monitor analytics to track and optimize website performance
• Brainstorm new and creative growth strategies
• Conduct competitor analysis and identify industry best practices in social media marketing
• Create and curate good quality, engaging content across different social media platforms (Facebook, Twitter, LinkedIn, Instagram, Youtube)
• Stay up-to-date on the latest social media trends and best practices
• Suggest new and innovative ways to leverage social media for branding of products and business
• Write and optimize content for blogging and press releases
• Creatively use knowledge to earn high quality backlinks''',
                'requirements': '''Educational Qualifications:
• Bachelor's Degree in Computer Science, Information Technology, Marketing, or related field

Experience Requirements:
• Minimum 2+ years of experience as SMO/SEO Executive
• Engaged in all SEO and SMO activities

Technical Skills:
• Strong knowledge of search engine optimization process
• Strong understanding of latest Google Algorithms
• Knowledge of blogging and press releases
• Proficiency in SEO tools (Google Analytics, Search Console, SEMrush, Ahrefs, etc.)
• Understanding of social media platforms and their algorithms
• Knowledge of content management systems

Soft Skills:
• Exceptional communication, writing, and presentation skills
• Creative thinking and problem-solving abilities
• Analytical mindset with attention to detail
• Ability to work independently and meet deadlines''',
                'experience_criteria': '''• Minimum 2 years of professional experience in SEO/SMO
• Proven track record of improving website rankings and traffic
• Experience with social media marketing campaigns
• Knowledge of latest SEO trends and algorithm updates''',
                'min_salary': 250000,
                'max_salary': 400000,
                'currency': 'INR',
                'travel_required': False,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created: {job.title}'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠ Already exists: {job.title}'))

    def create_job_4(self, designations, dept, user, deadline):
        """ROR + Next.JS Developer"""
        job, created = JobDescription.objects.get_or_create(
            title='ROR + Next.JS Developer / Consultant',
            designation=designations['ROR Developer'],
            defaults={
                'department': dept,
                'employment_type': 'full_time',
                'experience_level': 'mid_level',
                'location': 'Ahmedabad',
                'work_mode': 'office',
                'number_of_vacancies': 1,
                'application_deadline': deadline,
                'status': 'active',
                'posted_by': user,
                'job_description': '''We are seeking an experienced Ruby on Rails (ROR) Developer with Next.JS expertise to join our development team. The ideal candidate will have 3+ years of experience building scalable web applications and a strong understanding of modern web technologies.''',
                'responsibilities': '''• Design, develop, and maintain web applications using Ruby on Rails and Next.JS
• Build efficient, testable, and reusable code
• Implement microservices architecture
• Work with databases like PostgreSQL, MySQL, and MongoDB
• Deploy applications on cloud platforms (AWS/Kubernetes)
• Participate in code reviews and maintain code quality
• Collaborate with cross-functional teams
• Contribute in all phases of the development lifecycle
• Follow test-driven development practices''',
                'requirements': '''Educational Qualifications:
• Bachelor's Degree in Computer Science, Information Technology, or related field

Experience Requirements:
• Minimum 3+ years as full-time ROR Developer
• Executed at least 7-8 projects in different domains

Technical Skills:
• Hands-on experience with Next.js and NestJS
• Hands-on experience with ROR and its frameworks
• Expert-level knowledge of JavaScript
• Familiarity with Microservices architecture
• Experience with test-driven development
• Knowledge of latest open standards and web technologies
• Good knowledge of PostgreSQL, MySQL, MongoDB
• Cloud deployment experience (AWS/Kubernetes)
• Strong *nix skills (Linux, FreeBSD, Mac OS X)

Soft Skills:
• Exceptional analytical and interpersonal skills
• Great understanding of client requirements
• Pleasant communication
• Very good interdepartmental coordination
• Innovative and out-of-box thinking''',
                'experience_criteria': '''• 3+ years of ROR development experience
• Next.JS knowledge is a plus
• 7-8 completed projects across different domains
• Experience with cloud deployments''',
                'min_salary': 500000,
                'max_salary': 1000000,
                'currency': 'INR',
                'travel_required': False,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created: {job.title}'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠ Already exists: {job.title}'))

    def create_job_5(self, designations, dept, user, deadline):
        """Python Developer"""
        job, created = JobDescription.objects.get_or_create(
            title='Python Developer',
            designation=designations['Python Developer'],
            defaults={
                'department': dept,
                'employment_type': 'full_time',
                'experience_level': 'junior',
                'location': 'Ahmedabad',
                'work_mode': 'office',
                'number_of_vacancies': 1,
                'application_deadline': deadline,
                'status': 'active',
                'posted_by': user,
                'job_description': '''We are looking for a skilled Python Developer with 2+ years of experience in building APIs and websites. The ideal candidate will have expertise in Python frameworks and a passion for creating efficient, scalable solutions.''',
                'responsibilities': '''• Develop and maintain Python-based applications, APIs, and websites
• Work with frameworks like Django, Flask, and FastAPI
• Implement caching solutions using Redis, Memcached
• Design and optimize database schemas
• Integrate AI solutions like ChatGPT, Gemini
• Build RESTful APIs and microservices
• Deploy applications on cloud platforms (AWS, Azure, DigitalOcean)
• Implement CI/CD pipelines
• Write clean, maintainable code following best practices
• Participate in code reviews and testing''',
                'requirements': '''Educational Qualifications:
• Bachelor's Degree in Computer Science, Information Technology, or related field

Experience: 2+ years as Python Developer in APIs and Websites
Projects: 4-5 projects in different domains

Technical Skills:
• Hands-on experience with Python and frameworks (Django, Flask, FastAPI)
• Experience with caching (Redis, Memcached)
• Relational databases (PostgreSQL, MySQL)
• Version control (Git, Bitbucket) and CI/CD
• Strong problem-solving and debugging skills
• Understanding of design patterns and testing methodologies
• Experience with AI integrations (ChatGPT, Gemini)
• Familiarity with RESTful APIs, microservices
• Cloud services (AWS, Azure, DigitalOcean)

Soft Skills:
• Exceptional analytical and interpersonal skills
• Great client understanding
• Pleasant communication
• Good interdepartmental coordination
• Innovative thinking''',
                'experience_criteria': '''• 2+ years Python development
• 4-5 completed projects
• API and web development experience
• Cloud deployment experience''',
                'min_salary': 300000,
                'max_salary': 600000,
                'currency': 'INR',
                'travel_required': False,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created: {job.title}'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠ Already exists: {job.title}'))

    def create_job_6(self, designations, dept, user, deadline):
        """PHP Developer"""
        job, created = JobDescription.objects.get_or_create(
            title='PHP Developer',
            designation=designations['PHP Developer'],
            defaults={
                'department': dept,
                'employment_type': 'full_time',
                'experience_level': 'mid_level',
                'location': 'Ahmedabad',
                'work_mode': 'office',
                'number_of_vacancies': 1,
                'application_deadline': deadline,
                'status': 'active',
                'posted_by': user,
                'job_description': '''We are seeking an experienced PHP Developer with 3+ years of expertise in building robust APIs and websites. The ideal candidate will have strong Laravel framework knowledge and experience across multiple projects.''',
                'responsibilities': '''• Develop and maintain PHP-based applications and APIs
• Build efficient, testable, and reusable PHP modules
• Work extensively with Laravel framework
• Implement front-end technologies (HTML5, CSS3, JavaScript, jQuery)
• Design and optimize database structures
• Integrate third-party APIs and services
• Contribute in all development lifecycle phases
• Write clean, well-documented code
• Participate in code reviews
• Debug and troubleshoot applications''',
                'requirements': '''Educational Qualifications:
• Bachelor's Degree in Computer Science, Information Technology, or related field

Experience: 3+ years as PHP Developer
Projects: 7-8 projects in different domains

Technical Skills:
• Hands-on experience with Laravel framework
• In-depth knowledge of Core PHP
• Knowledge in CakePHP, Zend, NodeJS, or Symfony (Plus Point)
• Good understanding of HTML5, CSS3, JavaScript, jQuery
• Database design and optimization
• RESTful API development
• Version control systems (Git)

Soft Skills:
• Exceptional analytical and interpersonal skills
• Great client understanding
• Pleasant communication
• Very good interdepartmental coordination
• Innovative and out-of-box thinking''',
                'experience_criteria': '''• 3+ years PHP development
• 7-8 completed projects
• Strong Laravel expertise
• API development experience''',
                'min_salary': 350000,
                'max_salary': 700000,
                'currency': 'INR',
                'travel_required': False,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created: {job.title}'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠ Already exists: {job.title}'))

    def create_job_7(self, designations, dept, user, deadline):
        """MERN Developer"""
        job, created = JobDescription.objects.get_or_create(
            title='MERN Stack Developer',
            designation=designations['MERN Developer'],
            defaults={
                'department': dept,
                'employment_type': 'full_time',
                'experience_level': 'mid_level',
                'location': 'Ahmedabad',
                'work_mode': 'office',
                'number_of_vacancies': 1,
                'application_deadline': deadline,
                'status': 'active',
                'posted_by': user,
                'job_description': '''We are looking for a talented MERN Stack Developer with 3+ years of experience to build scalable web applications. The ideal candidate will have expertise across MongoDB, Express.js, React, and Node.js.''',
                'responsibilities': '''• Develop full-stack web applications using MERN stack
• Build responsive front-end using React with Hooks and Redux
• Develop robust back-end APIs using Node.js and Express.js
• Design and optimize MongoDB database schemas
• Implement RESTful APIs and microservices
• Deploy applications on cloud platforms (AWS, Azure, DigitalOcean)
• Set up and maintain CI/CD pipelines
• Write unit and integration tests
• Collaborate with cross-functional teams
• Contribute in all development phases''',
                'requirements': '''Educational Qualifications:
• Bachelor's Degree in Computer Science, Information Technology, or related field

Experience: 3+ years as MERN Developer
Projects: 7-8 projects in different domains

Technical Skills:
• Frontend: React, React Hooks, Redux, component-driven architecture
• Backend: Node.js, Express.js, RESTful APIs, middleware
• Database: MongoDB & MySQL (schema design, indexing, aggregation, query optimization)
• Version Control: Git, Bitbucket
• Deployment & DevOps: AWS, Azure, DigitalOcean, CI/CD pipelines
• Other: HTML5, CSS3, JavaScript (ES6+), JSON, WebSockets
• Testing: Mocha, Chai, or Jest

Soft Skills:
• Exceptional analytical and interpersonal skills
• Great client understanding
• Pleasant communication
• Very good interdepartmental coordination
• Innovative thinking''',
                'experience_criteria': '''• 3+ years MERN stack development
• 7-8 completed projects
• Full-stack development experience
• Cloud deployment experience''',
                'min_salary': 400000,
                'max_salary': 800000,
                'currency': 'INR',
                'travel_required': False,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created: {job.title}'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠ Already exists: {job.title}'))

    def create_job_8(self, designations, dept, user, deadline):
        """Jr. Shopify Developer"""
        job, created = JobDescription.objects.get_or_create(
            title='Jr. Shopify Developer',
            designation=designations['Shopify Developer'],
            defaults={
                'department': dept,
                'employment_type': 'full_time',
                'experience_level': 'junior',
                'location': 'Ahmedabad',
                'work_mode': 'office',
                'number_of_vacancies': 1,
                'application_deadline': deadline,
                'status': 'active',
                'posted_by': user,
                'job_description': '''We are seeking a Junior Shopify Developer with 2+ years of experience to build and customize Shopify stores. The ideal candidate will have strong knowledge of Liquid, JavaScript, and Shopify best practices.''',
                'responsibilities': '''• Develop and customize Shopify themes using Liquid
• Write optimized Liquid, JavaScript & jQuery code
• Implement custom code and functionality
• Integrate commonly used Shopify apps
• Ensure responsive design across devices
• Work with Shopify REST API and GraphQL
• Communicate with clients regarding requirements
• Debug and troubleshoot Shopify stores
• Stay updated with latest Shopify standards
• Optimize store performance''',
                'requirements': '''Educational Qualifications:
• Bachelor's Degree in Computer Science, Information Technology, or related field

Experience: 2+ years as Shopify Developer
Projects: 5-6 projects in different domains

Technical Skills:
• Knowledge of latest Shopify standards & updates
• Complete knowledge of Liquid coding structure and syntax
• Write optimized Liquid, JavaScript & jQuery code
• Knowledge of JavaScript & jQuery (must)
• Knowledge of CSS & Responsive Design
• Ability to do custom code & functionality
• Knowledge of commonly used apps
• Understanding of Shopify's limitations
• Ability to communicate with clients
• REST API and Shopify GraphQL (added advantage)

Soft Skills:
• Excellent problem-solving and communication skills
• Teamwork abilities
• Ability to collaborate across departments and with clients
• Exceptional analytical skills
• Great client understanding
• Pleasant communication
• Innovative thinking''',
                'experience_criteria': '''• 2+ years Shopify development
• 5-6 completed Shopify projects
• Strong Liquid and JavaScript skills
• Client communication experience''',
                'min_salary': 250000,
                'max_salary': 450000,
                'currency': 'INR',
                'travel_required': False,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created: {job.title}'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠ Already exists: {job.title}'))

    def create_job_9(self, designations, dept, user, deadline):
        """Jr. HTML Developer"""
        job, created = JobDescription.objects.get_or_create(
            title='Jr. HTML Developer',
            designation=designations['HTML Developer'],
            defaults={
                'department': dept,
                'employment_type': 'full_time',
                'experience_level': 'junior',
                'location': 'Ahmedabad',
                'work_mode': 'office',
                'number_of_vacancies': 1,
                'application_deadline': deadline,
                'status': 'active',
                'posted_by': user,
                'job_description': '''We are looking for a Junior HTML Developer with 2+ years of experience to create pixel-perfect, responsive web interfaces. The ideal candidate will have strong skills in HTML5, CSS3, and modern front-end technologies.''',
                'responsibilities': '''• Convert design specs (Invision, Photoshop, Sketch, Figma) into pixel-perfect HTML5/CSS templates
• Develop responsive layouts using Bootstrap and CSS Grid
• Implement animations and interactive elements
• Write clean, semantic HTML5 code
• Create reusable CSS components using SASS/LESS
• Ensure cross-browser compatibility
• Optimize web pages for performance
• Collaborate with designers and developers
• Maintain code quality and standards
• Stay updated with latest web technologies''',
                'requirements': '''Educational Qualifications:
• Bachelor's Degree in Computer Science, Information Technology, or related field

Experience: 2+ years as HTML Developer
Projects: 4-5 projects in different domains

Technical Skills:
• Good hands-on experience with HTML5, CSS3, jQuery, JavaScript
• Animations and interactive elements
• Bootstrap (3, 4, 5) and SASS
• High level experience with UI layouts, SASS, LESS, CSS GRID system
• Ability to convert design specs into pixel-perfect templates
• Basic knowledge of Photoshop, Adobe XD, Figma (plus)
• Responsive design principles
• Cross-browser compatibility

Soft Skills:
• Dedicated, result-focused, flexible and creative
• Self-motivated and strong collaborator
• Ability to manage expectations and conflicting needs
• Attention to detail
• Good communication skills''',
                'experience_criteria': '''• 2+ years HTML/CSS development
• 4-5 completed projects
• Strong responsive design skills
• Design-to-code conversion experience''',
                'min_salary': 200000,
                'max_salary': 400000,
                'currency': 'INR',
                'travel_required': False,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created: {job.title}'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠ Already exists: {job.title}'))

    def create_job_10(self, designations, dept, user, deadline):
        """AI/ML Developer"""
        job, created = JobDescription.objects.get_or_create(
            title='AI/ML Developer',
            designation=designations['AI/ML Developer'],
            defaults={
                'department': dept,
                'employment_type': 'full_time',
                'experience_level': 'mid_level',
                'location': 'Ahmedabad',
                'work_mode': 'office',
                'number_of_vacancies': 1,
                'application_deadline': deadline,
                'status': 'active',
                'posted_by': user,
                'job_description': '''We are seeking an experienced AI/ML Developer with 3+ years of expertise in artificial intelligence and machine learning. The ideal candidate will have hands-on experience with LLM models, multi-agent platforms, and modern AI technologies.''',
                'responsibilities': '''• Develop and deploy AI/ML solutions and applications
• Work with LLM models (OpenAI, Gemini, Claude)
• Implement multi-agent platforms (Crew.AI, Langflow)
• Design and optimize prompts for AI models
• Implement Retrieval-Augmented Generation (RAG) workflows
• Process and analyze data for ML models
• Optimize algorithms for performance
• Develop and integrate APIs for AI services
• Deploy solutions using Docker and AWS
• Collaborate with cross-functional teams
• Contribute in all development phases''',
                'requirements': '''Educational Qualifications:
• Bachelor's Degree in Computer Science, Information Technology, or related field

Experience: 3+ years as AI/ML Developer
Projects: 5-6 projects in different domains

Technical Skills:
• Proven hands-on experience with LLM models (OpenAI, Gemini, Claude)
• Proficiency in Multi-Agent Platforms (Crew.AI, Langflow)
• Solid skills in Prompt Engineering
• Experience with Retrieval-Augmented Generation (RAG)
• Proficiency in Python, TensorFlow, PyTorch
• Machine learning and deep learning expertise
• Cloud services (AWS, Azure)
• API development and integration
• Docker and containerization
• Version control (Git)
• Understanding of data structures, algorithms, computer architecture

Soft Skills:
• Excellent problem-solving and communication skills
• Teamwork abilities
• Ability to collaborate across departments and with clients
• Exceptional analytical skills
• Great client understanding
• Pleasant communication
• Innovative and out-of-box thinking''',
                'experience_criteria': '''• 3+ years AI/ML development
• 5-6 completed AI/ML projects
• LLM integration experience
• Cloud deployment experience''',
                'min_salary': 600000,
                'max_salary': 1200000,
                'currency': 'INR',
                'travel_required': False,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created: {job.title}'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠ Already exists: {job.title}'))

    def create_job_11(self, designations, dept, user, deadline):
        """UI/UX Designer"""
        job, created = JobDescription.objects.get_or_create(
            title='UI/UX Designer (Mobile & Web)',
            designation=designations['UI/UX Designer'],
            defaults={
                'department': dept,
                'employment_type': 'full_time',
                'experience_level': 'junior',
                'location': 'Ahmedabad',
                'work_mode': 'office',
                'number_of_vacancies': 1,
                'application_deadline': deadline,
                'status': 'active',
                'posted_by': user,
                'job_description': '''We are looking for a creative UI/UX Designer with 2+ years of experience in designing mobile apps and websites. The ideal candidate will have a strong portfolio demonstrating user-centered design principles and modern design tools expertise.''',
                'responsibilities': '''• Gather and evaluate user requirements with product managers and engineers
• Illustrate design ideas using storyboards, process flows, and sitemaps
• Design graphic user interface elements (menus, tabs, widgets)
• Build page navigation buttons and search fields
• Develop UI mockups and prototypes showing site function and appearance
• Create original graphic designs (images, sketches, tables)
• Prepare and present rough drafts to internal teams and stakeholders
• Identify and troubleshoot UX problems (responsiveness)
• Conduct layout adjustments based on user feedback
• Adhere to style standards on fonts, colors, and images
• Examine previous design feedback and briefs for new projects
• Investigate web/mobile usage analytics and trend spotting
• Analyze questionnaire responses, field studies, interviews
• Create user experience with user needs in mind
• Conduct observational research
• Attend design and business strategy meetings''',
                'requirements': '''Educational Qualifications:
• Bachelor's Degree in Design, Computer Science, Information Technology, or related field

Experience: 2+ years as UI/UX Designer
Projects: 2-3 projects in different domains

Technical Skills:
• Proficiency in design tools (Figma, Adobe XD, Sketch, Photoshop, Illustrator)
• Strong understanding of user-centered design principles
• Experience with wireframing and prototyping
• Knowledge of responsive design
• Understanding of mobile and web design patterns
• Basic knowledge of HTML/CSS (plus)
• Experience with design systems
• User research and testing methodologies

Soft Skills:
• Strong visual design skills
• Excellent communication and presentation abilities
• Ability to work collaboratively
• Attention to detail
• Creative problem-solving
• Time management skills
• Ability to handle feedback constructively''',
                'experience_criteria': '''• 2+ years UI/UX design experience
• 2-3 completed design projects
• Portfolio demonstrating mobile and web design
• User research experience''',
                'min_salary': 300000,
                'max_salary': 600000,
                'currency': 'INR',
                'travel_required': False,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created: {job.title}'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠ Already exists: {job.title}'))

    def create_job_12(self, designations, dept, user, deadline):
        """Sr. Quality Analyst"""
        job, created = JobDescription.objects.get_or_create(
            title='Sr. Quality Analyst (Manual & Automation)',
            designation=designations['Quality Analyst'],
            defaults={
                'department': dept,
                'employment_type': 'full_time',
                'experience_level': 'senior',
                'location': 'Ahmedabad',
                'work_mode': 'office',
                'number_of_vacancies': 1,
                'application_deadline': deadline,
                'status': 'active',
                'posted_by': user,
                'job_description': '''We are seeking a Senior Quality Analyst with 4+ years of experience in both manual and automation testing. The ideal candidate will have expertise in testing web applications, APIs, and mobile applications with a strong understanding of QA methodologies.''',
                'responsibilities': '''• Conduct manual testing on various software applications
• Develop, maintain, and execute manual test cases and scripts
• Collaborate with cross-functional teams for requirements understanding
• Design and implement automated test scripts
• Execute and analyze automated test results
• Identify and report defects systematically
• Work closely with developers to reproduce, debug, and resolve issues
• Create comprehensive test plans and test strategies
• Perform regression, integration, and system testing
• Test web applications, APIs, and mobile applications
• Ensure quality standards are met throughout SDLC
• Mentor junior QA team members''',
                'requirements': '''Educational Qualifications:
• Bachelor's Degree in Computer Science, Information Technology, or related field

Experience: 4+ years as Quality Analyst
Projects: 4-5 projects in different domains

Technical Skills:
• Proven experience in manual and automation testing
• Strong knowledge of manual testing methodologies and best practices
• Proficiency in automated test script creation and maintenance
• Experience testing web applications, APIs, and mobile applications
• Solid understanding of SDLC and agile methodologies
• Knowledge of testing tools (Selenium, Appium, JMeter, Postman, etc.)
• Experience with test management tools (JIRA, TestRail, etc.)
• Understanding of CI/CD pipelines
• API testing experience
• Mobile testing (iOS/Android)

Soft Skills:
• Excellent problem-solving and analytical skills
• Strong communication and collaboration skills
• Attention to detail
• Ability to work in fast-paced environment
• Team player with leadership qualities''',
                'experience_criteria': '''• 4+ years QA experience
• 4-5 completed testing projects
• Both manual and automation expertise
• Web, API, and mobile testing experience''',
                'min_salary': 400000,
                'max_salary': 800000,
                'currency': 'INR',
                'travel_required': False,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created: {job.title}'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠ Already exists: {job.title}'))

    def create_job_13(self, designations, dept, user, deadline):
        """React Native Developer"""
        job, created = JobDescription.objects.get_or_create(
            title='Mobile App Developer - React Native',
            designation=designations['Mobile App Developer'],
            defaults={
                'department': dept,
                'employment_type': 'full_time',
                'experience_level': 'mid_level',
                'location': 'Ahmedabad',
                'work_mode': 'office',
                'number_of_vacancies': 1,
                'application_deadline': deadline,
                'status': 'active',
                'posted_by': user,
                'job_description': '''We are seeking an experienced React Native Developer with 3+ years of expertise in building cross-platform mobile applications. The ideal candidate will have strong knowledge of React.js, React Native, and modern JavaScript frameworks.''',
                'responsibilities': '''• Develop and maintain high-quality mobile applications using React Native
• Build scalable web applications using React.js
• Implement state management using Redux
• Utilize React Hooks for better component functionality
• Work with RESTful APIs and third-party integrations
• Collaborate with cross-functional teams
• Write clean, maintainable code
• Participate in code reviews
• Work with Git, JIRA, and Agile methodologies
• Follow Test-Driven Development (TDD) practices
• Optimize application performance
• Debug and troubleshoot issues
• Contribute in all development lifecycle phases''',
                'requirements': '''Educational Qualifications:
• Bachelor's Degree in Computer Science, Information Technology, or related field

Experience: 3+ years as Mobile App Developer
Projects: 7-8 projects in different domains

Technical Skills:
• Hands-on experience with React Native framework
• Strong knowledge of Laravel framework
• In-depth knowledge of Core PHP
• Proficiency in React.js for web applications
• Experience with Redux for state management
• Implementation of React Hooks
• Experience with Git, JIRA, Agile Methodologies
• Knowledge of Test-Driven Development (TDD)
• Experience building mobile apps utilizing web services (REST/JSON)
• Understanding of mobile app architecture
• Knowledge of app publishing (Play Store/App Store)

Soft Skills:
• Exceptional analytical and interpersonal skills
• Great understanding of client requirements
• Pleasant and professional communication
• Very good interdepartmental coordination
• Innovative and out-of-box thinking
• Ability to work independently and in teams
• Strong attention to detail''',
                'experience_criteria': '''• 3+ years React Native development
• 7-8 completed mobile app projects
• Cross-platform development experience
• Published apps on Play Store/App Store
• Agile/Scrum experience
• Strong portfolio of React Native applications''',
                'min_salary': 400000,
                'max_salary': 800000,
                'currency': 'INR',
                'travel_required': False,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created: {job.title}'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠ Already exists: {job.title}'))
