"""Canonical destinations for the three consolidated guide routes."""
BASE = 'https://deekeforbusiness.github.io/deekebiz-product-hub/'
REDIRECTS = {
    'guides/overdue-invoice-reminder-email-examples': 'guides/follow-up-overdue-invoices-politely/#templates',
    'guides/ai-prompt-library-categories': 'guides/notion-ai-prompt-library/#categories-tags',
    'guides/organize-chatgpt-prompts-notion': 'guides/notion-ai-prompt-library/',
}


def canonical_url(path):
    destination = REDIRECTS.get(path)
    if destination:
        return BASE + destination.split('#', 1)[0]
    return BASE + ('' if path == '.' else path + '/')
