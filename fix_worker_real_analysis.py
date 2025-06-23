#!/usr/bin/env python3
"""
Fix Universal Worker to do ACTUAL AI analysis instead of placeholder simulation
"""

def fix_worker_analysis():
    """Replace placeholder simulation with real AI analysis"""
    
    print("🔧 Fixing Universal Worker to do real AI analysis...")
    
    # Read the file
    with open('universal_worker_enhanced.py', 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Find and replace the placeholder _process_task method
    old_method = '''    def _process_task(self, task):
        """Process a single task (placeholder for now)"""
        task_id = task.get('task_id', 'unknown')
        card_name = task.get('card_name', 'Unknown Card')
        card_id = task.get('card_id') or task.get('card_uuid')  # Support both field names
        
        logger.info(f"🎯 Processing task {task_id}: {card_name}")
        self.active_tasks.add(task_id)
        
        try:
            # Simulate work (replace with actual analysis)
            time.sleep(2)
            
            # Submit results with required card_id field
            results = {
                'task_id': task_id,
                'worker_id': self.worker_id,
                'card_id': card_id,  # This was missing - required by API
                'status': 'completed',
                'results': {'placeholder': 'analysis_data'},
                'completed_at': datetime.now(timezone.utc).isoformat()
            }
            
            response = requests.post(
                f"{self.server_url}/api/enhanced_swarm/submit_results",
                json=results,
                timeout=30  # Increased timeout for enhanced API
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Task {task_id} completed successfully")
                self.completed_tasks.add(task_id)
            else:
                logger.error(f"❌ Failed to submit results for task {task_id}")
                logger.error(f"Response: {response.text}")  # Added error details
                
        except Exception as e:
            logger.error(f"❌ Task {task_id} failed: {e}")
        finally:
            self.active_tasks.discard(task_id)'''
    
    new_method = '''    def _process_task(self, task):
        """Process a single task with actual AI analysis"""
        task_id = task.get('task_id', 'unknown')
        card_name = task.get('card_name', 'Unknown Card')
        card_id = task.get('card_id') or task.get('card_uuid')
        components = task.get('components', [])
        card_data = task.get('card_data', {})
        
        logger.info(f"🎯 Processing task {task_id}: {card_name} (Components: {len(components)})")
        self.active_tasks.add(task_id)
        
        start_time = time.time()
        
        try:
            # Actual AI analysis using Ollama
            analysis_results = {}
            
            for component in components:
                logger.info(f"🔍 Analyzing {component} for {card_name}")
                
                # Create AI analysis prompt
                prompt = self._create_analysis_prompt(card_data, component)
                
                # Call Ollama for analysis
                try:
                    component_start = time.time()
                    response = ollama.chat(
                        model='llama3.2',  # Use available model
                        messages=[
                            {
                                'role': 'system',
                                'content': 'You are an expert Magic: The Gathering analyst. Provide detailed, accurate analysis in 2-3 paragraphs.'
                            },
                            {
                                'role': 'user', 
                                'content': prompt
                            }
                        ]
                    )
                    
                    analysis_time = time.time() - component_start
                    analysis_content = response['message']['content']
                    
                    analysis_results[component] = analysis_content
                    logger.info(f"✅ Completed {component} analysis in {analysis_time:.1f}s")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to analyze {component}: {e}")
                    analysis_results[component] = f"Analysis failed: {str(e)}"
            
            total_time = time.time() - start_time
            
            # Submit real results
            results = {
                'task_id': task_id,
                'worker_id': self.worker_id,
                'card_id': card_id,
                'status': 'completed',
                'results': analysis_results,  # Real analysis, not placeholder
                'model_info': {
                    'model': 'llama3.2',
                    'worker_type': self.worker_type,
                    'components_analyzed': len(analysis_results)
                },
                'execution_time': total_time,
                'completed_at': datetime.now(timezone.utc).isoformat()
            }
            
            response = requests.post(
                f"{self.server_url}/api/enhanced_swarm/submit_results",
                json=results,
                timeout=120  # Longer timeout for real analysis
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Task {task_id} completed successfully with {len(analysis_results)} components in {total_time:.1f}s")
                self.completed_tasks.add(task_id)
            else:
                logger.error(f"❌ Failed to submit results for task {task_id}")
                logger.error(f"Response: {response.text}")
                
        except Exception as e:
            logger.error(f"❌ Task {task_id} failed: {e}")
        finally:
            self.active_tasks.discard(task_id)
    
    def _create_analysis_prompt(self, card_data: dict, component: str) -> str:
        """Create AI analysis prompt for a specific component"""
        card_name = card_data.get('name', 'Unknown')
        mana_cost = card_data.get('mana_cost', '')
        type_line = card_data.get('type_line', '')
        oracle_text = card_data.get('oracle_text', '')
        
        base_info = f"""
Card: {card_name}
Mana Cost: {mana_cost}
Type: {type_line}
Text: {oracle_text}
"""
        
        # Component-specific prompts
        prompts = {
            'play_tips': f"{base_info}\\nProvide 3-4 strategic play tips for using this card effectively in Commander/EDH games. Focus on timing, positioning, and synergies.",
            'synergy_analysis': f"{base_info}\\nAnalyze what types of cards and strategies synergize well with this card in Commander. Include specific card examples and deck themes.",
            'budget_alternatives': f"{base_info}\\nSuggest 3-4 budget-friendly alternative cards that provide similar effects or fill similar roles. Include approximate prices and trade-offs.",
            'combo_suggestions': f"{base_info}\\nIdentify potential combo interactions and synergistic card combinations with this card. Explain how the combos work.",
            'format_analysis': f"{base_info}\\nAnalyze this card's effectiveness and role in different Magic formats, especially Commander/EDH. Compare power levels across formats.",
            'competitive_analysis': f"{base_info}\\nEvaluate this card's competitive viability and meta positioning in Commander. Discuss its place in the current meta.",
            'mulligan_considerations': f"{base_info}\\nProvide guidance on when to keep or mulligan hands containing this card. Consider different game situations.",
            'deck_archetypes': f"{base_info}\\nIdentify which Commander deck archetypes and strategies would want to include this card. Explain why it fits those strategies.",
            'power_level_assessment': f"{base_info}\\nAssess this card's power level from 1-10 and explain its impact on games. Consider both casual and competitive play.",
            'investment_outlook': f"{base_info}\\nAnalyze this card's collectible value and investment potential. Consider reprints, playability, and market trends."
        }
        
        return prompts.get(component, f"{base_info}\\nProvide detailed analysis of this card for the {component} aspect.")'''
    
    # Replace the method
    if old_method in content:
        content = content.replace(old_method, new_method)
        print("✅ Replaced placeholder _process_task method with real AI analysis")
    else:
        print("❌ Could not find exact placeholder method to replace")
        return False
    
    # Write the fixed content
    with open('universal_worker_enhanced.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Universal Worker Enhanced fixed!")
    print("🔄 Workers will now:")
    print("  - Use actual Ollama AI models for analysis")
    print("  - Process each component with custom prompts")
    print("  - Take realistic time (30s-2min per component)")
    print("  - Submit real analysis content, not placeholders")
    
    return True

if __name__ == "__main__":
    success = fix_worker_analysis()
    if success:
        print("\\n🎯 READY: Workers will now do real AI analysis!")
        print("💡 Restart your workers to see actual MTG analysis being generated!")
    else:
        print("\\n❌ Fix failed - manual intervention needed")
