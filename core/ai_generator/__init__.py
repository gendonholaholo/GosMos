import openai
import groq
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
import json
import os
from pathlib import Path

class ContentGenerator:
    def __init__(self, provider: str = "groq", api_key: Optional[str] = None):
        self.provider = provider
        self.api_key = api_key or os.getenv(f"{provider.upper()}_API_KEY")
        
        if provider == "groq":
            self.client = groq.Client(api_key=self.api_key)
        elif provider == "openai":
            openai.api_key = self.api_key
            self.client = openai
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def generate_caption(self, product_data: Dict, style: str = "casual") -> str:
        """
        Generate a product caption using AI.
        """
        prompt = f"""
        Generate a {style} TikTok caption for the following product:
        
        Title: {product_data.get('title', '')}
        Price: {product_data.get('price', '')}
        Description: {product_data.get('description', '')}
        
        The caption should be engaging and suitable for TikTok Shop.
        """
        
        if self.provider == "groq":
            response = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=150
            )
            return response.choices[0].message.content
        else:
            response = self.client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=150
            )
            return response.choices[0].message.content
    
    def generate_script(self, product_data: Dict, duration: int = 60) -> str:
        """
        Generate a video script using AI.
        """
        prompt = f"""
        Generate a {duration}-second TikTok video script for the following product:
        
        Title: {product_data.get('title', '')}
        Price: {product_data.get('price', '')}
        Description: {product_data.get('description', '')}
        
        The script should include:
        1. Hook (first 3 seconds)
        2. Product showcase
        3. Benefits and features
        4. Call to action
        
        Format the script with timestamps.
        """
        
        if self.provider == "groq":
            response = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
        else:
            response = self.client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content

class ContentAnalyzer:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def analyze_engagement(self, content: str) -> Dict:
        """
        Analyze content for engagement potential.
        """
        # TODO: Implement actual engagement analysis
        return {
            "readability_score": 0.85,
            "emotional_tone": "positive",
            "call_to_action_present": True,
            "hashtag_count": len([w for w in content.split() if w.startswith("#")])
        }
    
    def find_similar_content(self, content: str, reference_content: List[str]) -> List[Dict]:
        """
        Find similar content using semantic similarity.
        """
        content_embedding = self.model.encode(content)
        reference_embeddings = self.model.encode(reference_content)
        
        similarities = []
        for i, ref_embedding in enumerate(reference_embeddings):
            similarity = np.dot(content_embedding, ref_embedding) / (
                np.linalg.norm(content_embedding) * np.linalg.norm(ref_embedding)
            )
            similarities.append({
                "content": reference_content[i],
                "similarity": float(similarity)
            })
        
        return sorted(similarities, key=lambda x: x["similarity"], reverse=True)

class ContentOptimizer:
    def __init__(self, generator: ContentGenerator, analyzer: ContentAnalyzer):
        self.generator = generator
        self.analyzer = analyzer
    
    def optimize_content(self, content: str, target_metric: str = "engagement") -> str:
        """
        Optimize content for a specific metric.
        """
        analysis = self.analyzer.analyze_engagement(content)
        
        if target_metric == "engagement":
            # Generate variations and select the best one
            variations = [
                self.generator.generate_caption({"title": content}, style="casual"),
                self.generator.generate_caption({"title": content}, style="professional"),
                self.generator.generate_caption({"title": content}, style="funny")
            ]
            
            best_variation = max(
                variations,
                key=lambda x: self.analyzer.analyze_engagement(x)["readability_score"]
            )
            
            return best_variation
        else:
            raise ValueError(f"Unsupported target metric: {target_metric}")

class AIGenerator:
    def __init__(self, provider: str = "groq", api_key: Optional[str] = None):
        self.content_generator = ContentGenerator(provider, api_key)
        self.content_analyzer = ContentAnalyzer()
        self.content_optimizer = ContentOptimizer(
            self.content_generator,
            self.content_analyzer
        )
    
    def generate(self, content_type: str, data: Dict, **kwargs) -> str:
        """
        Generate content based on type and data.
        """
        if content_type == "caption":
            return self.content_generator.generate_caption(data, **kwargs)
        elif content_type == "script":
            return self.content_generator.generate_script(data, **kwargs)
        else:
            raise ValueError(f"Unsupported content type: {content_type}")
    
    def analyze(self, content: str) -> Dict:
        """
        Analyze content for various metrics.
        """
        return self.content_analyzer.analyze_engagement(content)
    
    def optimize(self, content: str, target_metric: str = "engagement") -> str:
        """
        Optimize content for specific metrics.
        """
        return self.content_optimizer.optimize_content(content, target_metric) 