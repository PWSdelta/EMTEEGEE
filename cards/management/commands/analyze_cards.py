"""
Django management command to run card analysis operations.
"""

from django.core.management.base import BaseCommand, CommandError
from cards.analysis_manager import analysis_manager
from cards.ollama_client import OllamaClient, ALL_COMPONENT_TYPES
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Manage card analysis operations'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['status', 'analyze', 'reset', 'test'],
            help='Action to perform'
        )
        parser.add_argument(
            '--uuid',
            type=str,
            help='UUID of specific card to analyze'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help='Limit number of cards to process'
        )
        parser.add_argument(
            '--component',
            type=str,
            choices=ALL_COMPONENT_TYPES,
            help='Analyze specific component type'
        )

    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'status':
            self.show_status()
        elif action == 'analyze':
            self.run_analysis(options)
        elif action == 'reset':
            self.reset_analysis(options)
        elif action == 'test':
            self.test_ollama()

    def show_status(self):
        """Show analysis progress statistics."""
        self.stdout.write(self.style.SUCCESS('Card Analysis Status'))
        self.stdout.write('=' * 50)
        
        progress = analysis_manager.get_analysis_progress()
        
        if not progress:
            self.stdout.write(self.style.ERROR('Failed to get analysis progress'))
            return
        
        self.stdout.write(f"Total cards: {progress['total_cards']}")
        self.stdout.write(f"Fully analyzed: {progress['fully_analyzed']}")
        self.stdout.write(f"In progress: {progress['in_progress']}")
        self.stdout.write(f"Not started: {progress['not_started']}")
        self.stdout.write(f"Completion: {progress['completion_percentage']:.1f}%")
        
        # Show some sample cards needing analysis
        needs_analysis = analysis_manager.get_cards_for_analysis(limit=5)
        if needs_analysis:
            self.stdout.write('\nSample cards needing analysis:')
            for card in needs_analysis:
                name = card.get('name', 'Unknown')
                analysis = card.get('analysis', {})
                count = analysis.get('component_count', 0)
                self.stdout.write(f"  - {name}: {count}/20 components")

    def run_analysis(self, options):
        """Run card analysis."""
        uuid = options.get('uuid')
        limit = options.get('limit', 10)
        component = options.get('component')
        
        if uuid:
            # Analyze specific card
            card = analysis_manager.get_card_by_uuid(uuid)
            if not card:
                raise CommandError(f'Card with UUID {uuid} not found')            
            name = card.get('name', uuid)
            self.stdout.write(f'Analyzing {name}...')
            
            # Set up progress logging for this card
            import logging
            logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
            
            if component:
                # Analyze specific component
                success = analysis_manager.generate_component(uuid, component)
                if success:
                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully generated {component} for {name}')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'Failed to generate {component} for {name}')
                    )
            else:
                # Analyze all components
                results = analysis_manager.generate_all_components(uuid)
                successful = sum(1 for success in results.values() if success)
                total = len(results)
                
                self.stdout.write(
                    self.style.SUCCESS(f'Generated {successful}/{total} components for {name}')
                )
                
                # Show failed components
                failed = [comp for comp, success in results.items() if not success]
                if failed:
                    self.stdout.write(
                        self.style.WARNING(f'Failed components: {", ".join(failed)}')
                    )
        else:
            # Analyze multiple cards
            cards = analysis_manager.get_cards_for_analysis(limit=limit)
            if not cards:
                self.stdout.write(self.style.SUCCESS('No cards need analysis'))
                return
            
            self.stdout.write(f'Analyzing {len(cards)} cards...')
            
            for i, card in enumerate(cards, 1):
                uuid = card.get('uuid')
                name = card.get('name', uuid)
                
                self.stdout.write(f'[{i}/{len(cards)}] Analyzing {name}...')
                
                if component:
                    # Analyze specific component for each card
                    success = analysis_manager.generate_component(uuid, component)
                    if success:
                        self.stdout.write(f'  ✓ Generated {component}')
                    else:
                        self.stdout.write(f'  ✗ Failed to generate {component}')
                else:
                    # Analyze all components for each card
                    results = analysis_manager.generate_all_components(uuid)
                    successful = sum(1 for success in results.values() if success)
                    total = len(results)
                    
                    self.stdout.write(f'  Generated {successful}/{total} components')

    def reset_analysis(self, options):
        """Reset analysis for cards."""
        uuid = options.get('uuid')
        
        if uuid:
            # Reset specific card
            card = analysis_manager.get_card_by_uuid(uuid)
            if not card:
                raise CommandError(f'Card with UUID {uuid} not found')
            
            name = card.get('name', uuid)
            success = analysis_manager.reset_card_analysis(uuid)
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS(f'Reset analysis for {name}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'Failed to reset analysis for {name}')
                )
        else:
            # Ask for confirmation before resetting all
            self.stdout.write(
                self.style.WARNING('This will reset ALL card analysis data!')
            )
            confirm = input('Are you sure? (yes/no): ')
            
            if confirm.lower() != 'yes':
                self.stdout.write('Aborted')
                return
            
            # This would be a dangerous operation, so we'll implement it later
            self.stdout.write(
                self.style.ERROR('Bulk reset not implemented yet for safety')
            )

    def test_ollama(self):
        """Test Ollama connectivity and models."""
        self.stdout.write(self.style.SUCCESS('Testing Ollama Connection'))
        self.stdout.write('=' * 50)
        
        client = OllamaClient()
        
        # Test connection
        if client.is_available():
            self.stdout.write(self.style.SUCCESS('✓ Ollama service is running'))
        else:
            self.stdout.write(self.style.ERROR('✗ Ollama service is not available'))
            return
        
        # Test models
        available_models = client.get_available_models()
        if available_models:
            self.stdout.write(f'Available models: {", ".join(available_models)}')
        else:
            self.stdout.write(self.style.WARNING('No models found'))
            return
        
        # Test with a sample card
        self.stdout.write('\nTesting with Sol Ring...')
        card = analysis_manager.get_card_by_uuid('fd1a6801-1b5c-4b9e-9f34-c6bec4b6b5a8')  # Common Sol Ring UUID
        
        if not card:
            self.stdout.write(self.style.WARNING('Sol Ring not found, skipping test'))
            return
        
        # Test generating a simple component
        self.stdout.write('Generating test component...')
        component_data = client.generate_component(card, 'play_tips')
        
        if component_data:
            self.stdout.write(self.style.SUCCESS('✓ Successfully generated test component'))
            self.stdout.write(f'Model used: {component_data["model_used"]}')
            self.stdout.write(f'Word count: {component_data["word_count"]}')
            self.stdout.write(f'Preview: {component_data["content"][:100]}...')
        else:
            self.stdout.write(self.style.ERROR('✗ Failed to generate test component'))
