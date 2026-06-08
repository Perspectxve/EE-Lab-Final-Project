import json, os, requests

SYSTEM = '''You are a robot task planner. Output JSON only.
Allowed actions: Navigate(target), Pick(object), Place(object,destination), Observe(target), Explore().
Pressing a button should be represented as Navigate(button), Place(nothing, button).
A zone like "bird zone" means the tabletop/region near the bird picture/sign.
Never output motor commands. Use known entities when possible. If an entity is unknown, still name it naturally so the executor can search.'''

MOCK_PLAN = [{"action":"Explore"}]

def extract_json(text):
    s = text.strip()
    if s.startswith('```'):
        s = s.split('```')[1]
        if s.lstrip().startswith('json'): s = s.lstrip()[4:]
    start = s.find('['); end = s.rfind(']')
    if start >= 0 and end > start: return json.loads(s[start:end+1])
    start = s.find('{'); end = s.rfind('}')
    if start >= 0 and end > start: return json.loads(s[start:end+1])
    raise ValueError('No JSON found in LLM output')

def plan_with_llm(command, world, provider='mock', gemini_model='gemini-1.5-flash', ollama_model='qwen2.5:7b', ollama_url='http://localhost:11434/api/generate'):
    prompt = f"{SYSTEM}\n\nWorld model:\n{world}\n\nUser instruction: {command}\n\nReturn a JSON array of actions."
    if provider == 'mock':
        return MOCK_PLAN
    if provider == 'ollama':
        r = requests.post(ollama_url, json={'model': ollama_model, 'prompt': prompt, 'stream': False}, timeout=60)
        r.raise_for_status()
        return extract_json(r.json().get('response',''))
    if provider == 'gemini':
        import google.generativeai as genai
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key: raise RuntimeError('Set GEMINI_API_KEY')
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(gemini_model)
        resp = model.generate_content(prompt)
        return extract_json(resp.text)
    raise ValueError(f'Unknown provider {provider}')
