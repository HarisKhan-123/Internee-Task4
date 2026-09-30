"""
Synthetic training data for the career-cluster classifier.

Each entry is a short text (a blend of skills + interests, the way a
profile will be flattened before scoring) paired with the career
cluster it most represents. This is NOT meant to be exhaustive - it is
a small, hand-authored seed set large enough to train a lightweight
text classifier that narrows a profile down to a handful of plausible
clusters, which the LLM step then turns into concrete roles and a
learning path.

Add more rows any time recommendations look off for a category you
care about, then re-run `python -m model.train_classifier`.
"""

CATEGORIES = [
    "Software Engineering",
    "Data Science & Machine Learning",
    "Embedded Systems & IoT",
    "Cybersecurity",
    "Cloud & DevOps",
    "UX / UI Design",
    "Product Management",
    "Digital Marketing & SEO",
    "Technical Writing & Content",
    "Business & Data Analysis",
]

# (text, label) pairs
TRAINING_DATA = [
    # Software Engineering
    ("python java c++ algorithms data structures building apps", "Software Engineering"),
    ("javascript react node backend apis web development", "Software Engineering"),
    ("object oriented programming debugging git github open source", "Software Engineering"),
    ("mobile app development android kotlin flutter ios swift", "Software Engineering"),
    ("competitive programming leetcode building side projects coding", "Software Engineering"),
    ("full stack development databases rest apis software design", "Software Engineering"),
    ("writing clean code unit testing software architecture", "Software Engineering"),
    ("building a saas product from scratch programming logic puzzles", "Software Engineering"),

    # Data Science & Machine Learning
    ("python pandas numpy statistics machine learning models", "Data Science & Machine Learning"),
    ("deep learning neural networks tensorflow pytorch training models", "Data Science & Machine Learning"),
    ("data analysis visualization jupyter notebooks predictive modeling", "Data Science & Machine Learning"),
    ("nlp computer vision ai research kaggle competitions", "Data Science & Machine Learning"),
    ("sql data cleaning feature engineering regression classification", "Data Science & Machine Learning"),
    ("statistics probability experimenting with ml algorithms", "Data Science & Machine Learning"),
    ("building recommendation systems and analyzing large datasets", "Data Science & Machine Learning"),

    # Embedded Systems & IoT
    ("embedded c microcontrollers arduino raspberry pi circuits", "Embedded Systems & IoT"),
    ("fpga verilog vhdl digital logic hardware design", "Embedded Systems & IoT"),
    ("iot sensors wireless communication firmware development", "Embedded Systems & IoT"),
    ("pcb design soldering robotics electronics projects", "Embedded Systems & IoT"),
    ("real time operating systems rtos low level programming", "Embedded Systems & IoT"),
    ("building smart devices sensor networks hardware tinkering", "Embedded Systems & IoT"),
    ("networking protocols communication systems signal processing", "Embedded Systems & IoT"),

    # Cybersecurity
    ("network security penetration testing ethical hacking ctf", "Cybersecurity"),
    ("cryptography vulnerability analysis security tools linux", "Cybersecurity"),
    ("malware analysis reverse engineering security audits", "Cybersecurity"),
    ("firewalls intrusion detection systems threat hunting", "Cybersecurity"),
    ("bug bounty hunting web application security ctf competitions", "Cybersecurity"),
    ("securing systems risk assessment compliance security research", "Cybersecurity"),

    # Cloud & DevOps
    ("aws azure docker kubernetes ci cd pipelines cloud infrastructure", "Cloud & DevOps"),
    ("linux servers automation scripting infrastructure as code", "Cloud & DevOps"),
    ("terraform ansible deployment monitoring cloud architecture", "Cloud & DevOps"),
    ("site reliability scaling systems container orchestration", "Cloud & DevOps"),
    ("build pipelines automation devops culture cloud cost optimization", "Cloud & DevOps"),

    # UX / UI Design
    ("figma wireframes user research prototyping visual design", "UX / UI Design"),
    ("interaction design usability testing design systems", "UX / UI Design"),
    ("graphic design typography color theory branding", "UX / UI Design"),
    ("designing mobile app interfaces user experience research", "UX / UI Design"),
    ("sketching mockups accessibility human centered design", "UX / UI Design"),

    # Product Management
    ("roadmaps stakeholder communication prioritization product strategy", "Product Management"),
    ("user stories agile scrum backlog grooming product sense", "Product Management"),
    ("market research feature planning cross functional collaboration", "Product Management"),
    ("analyzing user needs and translating them into product requirements", "Product Management"),
    ("leading teams organizing projects business strategy planning", "Product Management"),

    # Digital Marketing & SEO
    ("seo keyword research content strategy blogging google analytics", "Digital Marketing & SEO"),
    ("social media marketing campaigns branding audience growth", "Digital Marketing & SEO"),
    ("email marketing copywriting conversion optimization ads", "Digital Marketing & SEO"),
    ("growth hacking link building on page optimization seo audits", "Digital Marketing & SEO"),
    ("running paid ad campaigns analytics driven marketing funnels", "Digital Marketing & SEO"),

    # Technical Writing & Content
    ("technical writing documentation blogging clear explanations", "Technical Writing & Content"),
    ("ghostwriting content creation editing storytelling for brands", "Technical Writing & Content"),
    ("writing tutorials api documentation developer guides", "Technical Writing & Content"),
    ("research and writing long form articles explaining complex topics simply", "Technical Writing & Content"),
    ("content strategy editorial calendars writing for the web", "Technical Writing & Content"),

    # Business & Data Analysis
    ("excel dashboards business reporting kpis financial analysis", "Business & Data Analysis"),
    ("power bi tableau data storytelling business intelligence", "Business & Data Analysis"),
    ("market analysis competitor research business case studies", "Business & Data Analysis"),
    ("process improvement operations analytics spreadsheets modeling", "Business & Data Analysis"),
    ("analyzing business metrics forecasting and reporting trends", "Business & Data Analysis"),
]
