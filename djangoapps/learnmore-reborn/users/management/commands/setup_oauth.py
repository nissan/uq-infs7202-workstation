from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp


class Command(BaseCommand):
    help = 'Sets up Site and SocialApp for OAuth authentication'

    def add_arguments(self, parser):
        parser.add_argument('--domain', type=str, default='localhost:8000',
                            help='Domain name for the site')
        parser.add_argument('--name', type=str, default='LearnMore',
                            help='Display name for the site')
        parser.add_argument('--client-id', type=str,
                            help='Google OAuth client ID')
        parser.add_argument('--client-secret', type=str,
                            help='Google OAuth client secret')

    def handle(self, *args, **options):
        # Configure Site
        site, created = Site.objects.get_or_create(pk=1)
        site.domain = options['domain']
        site.name = options['name']
        site.save()
        
        self.stdout.write(self.style.SUCCESS(
            f"{'Created' if created else 'Updated'} Site: {site.name} ({site.domain})"
        ))
        
        # Configure SocialApp if client ID and secret provided
        if options['client_id'] and options['client_secret']:
            social_app, created = SocialApp.objects.get_or_create(
                provider='google',
                defaults={
                    'name': 'Google',
                    'client_id': options['client_id'],
                    'secret': options['client_secret'],
                }
            )
            
            if not created:
                social_app.client_id = options['client_id']
                social_app.secret = options['client_secret']
                social_app.save()
            
            # Make sure the social app is associated with the site
            social_app.sites.add(site)
            
            self.stdout.write(self.style.SUCCESS(
                f"{'Created' if created else 'Updated'} Google SocialApp and associated with {site.name}"
            ))
        else:
            self.stdout.write(self.style.WARNING(
                "No client ID or secret provided. Set these up manually in the admin interface, "
                "or run this command with --client-id and --client-secret options."
            ))
            
        self.stdout.write(self.style.SUCCESS(
            "\nOAuth setup complete. To fully use Google authentication, make sure you have:"
            "\n1. Added GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET to your .env file"
            "\n2. Configured correct redirect URIs in Google Cloud Console"
            "\n3. Set up proper HTTPS in production"
        ))