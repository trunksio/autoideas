"""
AI processing module for AutoIdeas
Handles transcript processing, clustering, and theme generation
"""

import json
import logging
import os
from typing import Dict, Any, List, Optional
import openai
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np

logger = logging.getLogger(__name__)


class AIProcessor:
    """AI processor for idea analysis and clustering"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key
    
    def process_transcript(
        self,
        transcript: str,
        question_id: str,
        workshop_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process voice transcript into structured idea
        
        Args:
            transcript: Voice transcript text
            question_id: Question identifier
            workshop_config: Workshop configuration
            
        Returns:
            Processed idea data
        """
        try:
            # Get question context
            questions = workshop_config.get("elevenlabs", {}).get("questions", [])
            question_context = self._get_question_context(question_id, questions)
            
            # Determine category based on question
            category = self._determine_category(question_id, question_context)
            
            # Extract key points (using simple processing for now)
            processed = {
                "original_transcript": transcript,
                "question_id": question_id,
                "category": category,
                "title": self._generate_title(transcript),
                "description": self._clean_transcript(transcript),
                "key_points": self._extract_key_points(transcript),
                "sentiment": self._analyze_sentiment(transcript)
            }
            
            # If OpenAI is configured, use it for better processing
            if self.api_key:
                processed = self._process_with_ai(
                    transcript,
                    question_context,
                    category
                )
                processed["question_id"] = question_id
                processed["category"] = category
            
            return processed
            
        except Exception as e:
            logger.error(f"Error processing transcript: {e}")
            # Return basic processing as fallback
            return {
                "original_transcript": transcript,
                "question_id": question_id,
                "category": "general",
                "title": transcript[:50] + "..." if len(transcript) > 50 else transcript,
                "description": transcript,
                "key_points": [transcript],
                "sentiment": "neutral"
            }
    
    def _process_with_ai(
        self,
        transcript: str,
        question_context: str,
        category: str
    ) -> Dict[str, Any]:
        """
        Process transcript using OpenAI
        
        Args:
            transcript: Voice transcript
            question_context: Question being answered
            category: Idea category
            
        Returns:
            AI-processed idea data
        """
        try:
            prompt = f"""
            Process this voice response into a structured idea.
            
            Question: {question_context}
            Category: {category}
            Response: {transcript}
            
            Extract and return in JSON format:
            1. title: A clear, concise title (max 10 words)
            2. description: A refined description of the idea
            3. key_points: List of 2-3 key points
            4. opportunity_statement: Reframe as an opportunity (start with "How might we...")
            5. impact_area: Primary area of impact (operations, member_experience, compliance, efficiency)
            6. sentiment: Overall sentiment (positive, neutral, negative, mixed)
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert at processing workshop ideas and feedback."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            # Parse AI response
            ai_result = json.loads(response.choices[0].message.content)
            
            return {
                "original_transcript": transcript,
                "title": ai_result.get("title", "New Idea"),
                "description": ai_result.get("description", transcript),
                "key_points": ai_result.get("key_points", []),
                "opportunity_statement": ai_result.get("opportunity_statement", ""),
                "impact_area": ai_result.get("impact_area", "general"),
                "sentiment": ai_result.get("sentiment", "neutral")
            }
            
        except Exception as e:
            logger.error(f"Error with AI processing: {e}")
            # Fallback to basic processing
            return {
                "original_transcript": transcript,
                "title": self._generate_title(transcript),
                "description": transcript,
                "key_points": self._extract_key_points(transcript),
                "sentiment": "neutral"
            }
    
    def cluster_ideas(self, ideas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Cluster similar ideas together
        
        Args:
            ideas: List of processed ideas
            
        Returns:
            Clustered ideas with cluster labels
        """
        try:
            if len(ideas) < 3:
                # Not enough ideas to cluster
                return [{
                    "cluster_id": 0,
                    "ideas": ideas,
                    "size": len(ideas)
                }]
            
            # Extract text for clustering
            texts = [
                f"{idea.get('title', '')} {idea.get('description', '')}"
                for idea in ideas
            ]
            
            # Vectorize texts
            vectorizer = TfidfVectorizer(
                max_features=100,
                stop_words='english',
                ngram_range=(1, 2)
            )
            X = vectorizer.fit_transform(texts)
            
            # Determine optimal number of clusters (max 5)
            n_clusters = min(5, max(2, len(ideas) // 3))
            
            # Perform clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(X)
            
            # Group ideas by cluster
            clusters = []
            for i in range(n_clusters):
                cluster_ideas = [
                    ideas[j] for j, label in enumerate(cluster_labels) if label == i
                ]
                clusters.append({
                    "cluster_id": i,
                    "ideas": cluster_ideas,
                    "size": len(cluster_ideas),
                    "centroid": self._get_cluster_centroid(cluster_ideas)
                })
            
            return clusters
            
        except Exception as e:
            logger.error(f"Error clustering ideas: {e}")
            return [{
                "cluster_id": 0,
                "ideas": ideas,
                "size": len(ideas)
            }]
    
    def generate_themes(self, clusters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate themes for idea clusters
        
        Args:
            clusters: Clustered ideas
            
        Returns:
            Themes for each cluster
        """
        themes = []
        
        for cluster in clusters:
            # Extract common words/phrases
            ideas_text = " ".join([
                f"{idea.get('title', '')} {idea.get('description', '')}"
                for idea in cluster["ideas"]
            ])
            
            theme = {
                "cluster_id": cluster["cluster_id"],
                "theme_name": self._generate_theme_name(cluster["ideas"]),
                "description": self._generate_theme_description(cluster["ideas"]),
                "idea_count": cluster["size"],
                "key_topics": self._extract_topics(ideas_text)
            }
            
            themes.append(theme)
        
        return themes
    
    def _get_question_context(self, question_id: str, questions: List[Dict]) -> str:
        """Get question text from configuration"""
        for q in questions:
            if q.get("id") == question_id:
                return q.get("text", "")
        return ""
    
    def _determine_category(self, question_id: str, question_context: str) -> str:
        """Determine category based on question"""
        categories = {
            "workflow": "workflow_friction",
            "member": "member_experience",
            "decision": "decision_support",
            "wish": "wishlist"
        }
        
        question_lower = question_context.lower()
        for key, category in categories.items():
            if key in question_lower:
                return category
        
        return "general"
    
    def _generate_title(self, text: str) -> str:
        """Generate a title from text"""
        # Simple approach: take first sentence or first 50 chars
        sentences = text.split('.')
        if sentences:
            title = sentences[0].strip()
            if len(title) > 50:
                title = title[:47] + "..."
            return title
        return text[:50] + "..." if len(text) > 50 else text
    
    def _clean_transcript(self, text: str) -> str:
        """Clean and format transcript text"""
        # Remove extra whitespace
        text = " ".join(text.split())
        # Capitalize first letter
        if text:
            text = text[0].upper() + text[1:]
        return text
    
    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key points from text"""
        # Simple approach: split by sentences and take first 3
        sentences = text.split('.')
        key_points = []
        for sentence in sentences[:3]:
            sentence = sentence.strip()
            if sentence:
                key_points.append(sentence)
        return key_points if key_points else [text]
    
    def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of text"""
        # Simple keyword-based sentiment analysis
        positive_words = ["good", "great", "excellent", "love", "wonderful", "fantastic", "better"]
        negative_words = ["bad", "terrible", "hate", "awful", "worse", "problem", "issue", "difficult"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        elif positive_count > 0 and negative_count > 0:
            return "mixed"
        return "neutral"
    
    def _get_cluster_centroid(self, ideas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get representative idea for cluster"""
        # Return the idea with the longest description as representative
        if not ideas:
            return {}
        return max(ideas, key=lambda x: len(x.get("description", "")))
    
    def _generate_theme_name(self, ideas: List[Dict[str, Any]]) -> str:
        """Generate theme name for cluster"""
        # Use most common words from titles
        titles = " ".join([idea.get("title", "") for idea in ideas])
        words = titles.lower().split()
        
        # Remove common words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for"}
        words = [w for w in words if w not in stop_words and len(w) > 3]
        
        if words:
            # Return most common word as theme
            from collections import Counter
            most_common = Counter(words).most_common(1)
            if most_common:
                return most_common[0][0].capitalize() + " Theme"
        
        return "General Theme"
    
    def _generate_theme_description(self, ideas: List[Dict[str, Any]]) -> str:
        """Generate theme description"""
        return f"Collection of {len(ideas)} related ideas focusing on similar topics and opportunities"
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract key topics from text"""
        # Simple noun extraction
        words = text.lower().split()
        
        # Remove common words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "is", "are", "was", "were"}
        words = [w for w in words if w not in stop_words and len(w) > 3]
        
        # Get top 5 most common words
        from collections import Counter
        most_common = Counter(words).most_common(5)
        
        return [word for word, _ in most_common]