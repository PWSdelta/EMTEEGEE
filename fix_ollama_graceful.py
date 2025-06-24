#!/usr/bin/env python3
"""
Quick fix: Make worker handle missing Ollama gracefully
"""

def fix_worker_ollama_check():
    """Add Ollama availability check to worker"""
    
    print("🔧 Adding Ollama availability check to worker...")
    
    with open('universal_worker_enhanced.py', 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Add Ollama check method after imports
    ollama_check_method = '''
    def _check_ollama_available(self):
        """Check if Ollama is available for AI analysis"""
        try:
            import ollama
            # Test if Ollama service is running
            ollama.list()  # This will fail if service isn't running
            return True
        except Exception as e:
            logger.warning(f"⚠️  Ollama not available: {e}")
            return False
'''
    
    # Add the method after the __init__ method
    if '_check_ollama_available' not in content:
        # Find the end of __init__ method
        init_end = content.find('def register(self)')
        if init_end > 0:
            content = content[:init_end] + ollama_check_method + '\n    ' + content[init_end:]
    
    # Modify the AI analysis to check Ollama first
    old_ai_code = '''                # Call Ollama AI
                    response = ollama.chat(
                        model='llama3.2',
                        messages=[
                            {'role': 'system', 'content': 'You are an expert Magic: The Gathering analyst.'},
                            {'role': 'user', 'content': prompt}
                        ]
                    )
                    
                    analysis_results[component] = response['message']['content']
                    logger.info(f"✅ Completed {component} analysis")'''
    
    new_ai_code = '''                # Check if Ollama is available, fallback to placeholder if not
                    if self._check_ollama_available():
                        try:
                            response = ollama.chat(
                                model='llama3.2',
                                messages=[
                                    {'role': 'system', 'content': 'You are an expert Magic: The Gathering analyst.'},
                                    {'role': 'user', 'content': prompt}
                                ]
                            )
                            analysis_results[component] = response['message']['content']
                            logger.info(f"✅ Completed {component} AI analysis")
                        except Exception as e:
                            logger.warning(f"⚠️  Ollama failed, using placeholder: {e}")
                            analysis_results[component] = f"[AI analysis placeholder for {component} - Ollama service unavailable]"
                    else:
                        logger.info(f"📝 Using placeholder for {component} (Ollama not available)")
                        analysis_results[component] = f"[AI analysis placeholder for {component} - Ollama not installed]"'''
    
    if old_ai_code in content:
        content = content.replace(old_ai_code, new_ai_code)
        print("✅ Added Ollama availability check")
    else:
        print("❌ Could not find AI code to modify")
        return False
    
    # Write the fixed content
    with open('universal_worker_enhanced.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Worker now handles missing Ollama gracefully!")
    return True

if __name__ == "__main__":
    success = fix_worker_ollama_check()
    if success:
        print("\n🎯 FIXED: Workers will now work even without Ollama")
        print("💡 Django should start normally now")
        print("🔄 Install Ollama later for real AI analysis")
    else:
        print("\n❌ Fix failed - may need manual intervention")
