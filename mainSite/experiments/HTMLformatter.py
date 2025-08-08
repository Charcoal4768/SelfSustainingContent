from html import escape

def format_article_html(article: dict) -> str:
    title = escape(article.get("title", ""))
    tags = article.get("Tags", [])
    sections = article.get("article_body", {}).get("Sections", [])

    # raw_desc = ""
    # if sections:
    #     raw_desc = sections[0].get("content", "").strip().replace('\n', ' ')
    description = article.get("description","A very cool article!")

    tags_text = ', '.join([escape(tag) for tag in tags])

    html_head = {
        f'<meta name="description" content="{description}">',
        f'<meta name="robots" content="index, follow">',
        f'<meta property="og:title" content="{title} | The Unfiltered">',
        f'<meta property="og:description" content="{description}">',
        f'<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{title}">',
        f'<meta name="twitter:description" content="{description}">',
        f'<meta name="keywords" content="{tags_text}">'
    }
    html_body = [
        '<div class="article-container">',
        '<div class="vertical-layer">',
        f'<h1 class="article-heading animate right visible">{title}</h1>',
        '<div class="tags-container">'
    ]

    for tag in tags:
        tag = escape(tag)
        html_body.append(f'<p class="tag animate right visible">{tag}</p>')
    
    html_body.append('</div>')  # close tags-container
    html_body.append('</div>')  # close vertical-layer
    html_body.append('<div class="article-body">')

    for section in sections:
        heading = escape(section.get("heading", ""))
        content = section.get("content", "")
        paragraphs = content.split('\n')

        html_body.append('<div class="section">')
        html_body.append(f'<h2 class="article-subheading">{heading}</h2>')
        html_body.append('<div class="content">')
        
        for para in paragraphs:
            para = escape(para.strip())
            if para:
                html_body.append(f'<p class="article-bodytext animate right">{para}</p>')

        html_body.append('</div>')  # close content
        html_body.append('</div>')  # close section

    html_body.append('</div>')  # close article-body
    html_body.append('</div>')  # close article-container

    return [title,''.join(html_head),''.join(html_body)]

# Example usage (mock):
if __name__ == '__main__':
    example_article = {
        "title": "Sample Title",
        "Tags": ["tag1", "tag2"],
        "article_body": {
            "Sections": [
                {"heading": "Intro", "content": "Paragraph 1\nParagraph 2"},
                {"heading": "Conclusion", "content": "Final thoughts here."}
            ]
        },
        "description":"Some attention catching, shocking sentence"
    }

    formatted_html = format_article_html(example_article)
    print(formatted_html)
