# SelfSustainingContent

**Full-stack Flask platform for automated, AI-driven content generation.**
Please leave a star if you like my project! :)

## Intro

SelfSustainingContent is a robust, modular pipeline for generating high-quality, SEO-optimized articles and titlesz all hands-free. Designed for scalability and maintainability, this project streamlines every step of the ingest-to-deploy flow, leveraging advanced NLP, real-time data, and dynamic templating.

Some screenshots:

# The admin panel:

<img width="1900" height="990" alt="image" src="https://github.com/user-attachments/assets/646b0b72-5e19-45ce-a809-d5b304f30733" />

# Generated article in admin panel

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/d7ffd531-3363-4e69-bb3e-e5608d1e51f8" />

# Published article in the ```/posts/``` route:

<img width="1906" height="1079" alt="image" src="https://github.com/user-attachments/assets/f3ae5fd6-c7fa-4ee0-82d8-3e1c2ac2077c" />

## Features

- **Automated Content Generation:** Produces well-structured, SEO-friendly pages and articles using modular generator utilities.
- **Scalable Architecture:** Built for growth, with isolated Python modules in the `generator` package allowing for easy testing, debugging, and reuse.
- **SEO Optimization:** Every page and title is crafted with SEO best practices, including keyword integration, fast loading, and semantic HTML.
- **Real-Time Data Integration:** Dynamic content sources and up-to-date information incorporated into each article.
- **Sentiment Analysis & Formatting:** Integrated NLP pipelines ensure content is engaging, relevant, and readable.
- **Hands-Free Publishing:** From scraping to deployment, the platform automates the entire workflow.
- **Maintainable Codebase:** Components are organized for clarity and extensibility, making onboarding and upgrades straightforward.
- **Authentication (In Progress):** Currently implementing user authentication using `werkzeug.security` for secure access and management.

## Project Structure

```
SelfSustainingContent/
├── generator/        # Modular utilities for content generation, scraping, NLP, formatting, etc.
├── static/           # CSS, JS, and images for frontend
├── templates/        # Dynamic Jinja/Mako templates for articles and pages
├── app.py            # Main Flask application
├── requirements.txt  # Python dependencies
└── README.md
```
- The `generator` package is the core for easy content generation: each submodule is isolated for easy debugging, testing, and reuse.
- Frontend templates are optimized for SEO and fast loading.
- All data for all articles is scraped from organic sources such as reddit posts, this makes sure that it reflects real user opinion.
- You can give additional information to the LLM to use in diffrent stages of the content generation, making it suitable for multiple diffrent types and styles of articles

## Roadmap

- Polish authentication and user management features
- Add comment system and search feature (groundwork is already laid out)
- Minor CSS refactoring editable feilds
- Add more branding and a site logo
- Expand content sources and NLP tools
- Enhance testing and CI/CD workflows
- Add admin dashboard and analytics
- Future plans: Use APScheduler to schedule content upload, get approved for adsense and insert ads.

## Contributing

I initially made this project as a personal project and as something to put on my resume but... Contributions welcome! Infact, more than welcome! Please submit pull requests or open issues for suggestions, bug reports, or feature requests.

I would really appreciate any help with refactroing the code, cleaning things up or making slow code faster, adding new features, etc. if you want to help then this is how you can contribute:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Charcoal4768/SelfSustainingContent.git
   cd SelfSustainingContent
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Flask app:**
   ```bash
   python app.py
   ```

## License

[MIT](LICENSE)

---
