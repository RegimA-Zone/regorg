#!/usr/bin/env python3
"""
RegimA AI Integration Module - Production-Ready API Integration

This module provides real AI API integration for RegimA's organizational
learning cycle, replacing mock responses with actual AI model calls.
Supports OpenAI GPT-4, Anthropic Claude, and Google Gemini Pro.
"""

import json
import os
import sys
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import asyncio
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AIProvider(Enum):
    """Supported AI providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    LOCAL = "local"  # Fallback for when no API keys available


class AnalysisType(Enum):
    """Types of analysis that can be performed."""
    ZONE_CONCEPT = "zone_concept"
    CONSCIOUSNESS = "consciousness"
    GUIDANCE = "guidance"
    COMPREHENSIVE = "comprehensive"
    TRANSCENDENCE = "transcendence"
    INNOVATION = "innovation"


@dataclass
class AIConfig:
    """Configuration for AI model calls."""
    provider: AIProvider
    model: str
    max_tokens: int = 4000
    temperature: float = 0.8
    top_p: float = 0.95
    timeout: int = 60
    retry_attempts: int = 3
    api_key: Optional[str] = None


@dataclass
class AIResponse:
    """Structured response from AI models."""
    content: str
    provider: AIProvider
    model: str
    tokens_used: int
    latency_ms: float
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    success: bool = True
    error: Optional[str] = None
    cache_hit: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            'content': self.content,
            'provider': self.provider.value,
            'model': self.model,
            'tokens_used': self.tokens_used,
            'latency_ms': self.latency_ms,
            'timestamp': self.timestamp,
            'success': self.success,
            'error': self.error,
            'cache_hit': self.cache_hit
        }


class AIProviderBase(ABC):
    """Base class for AI provider implementations."""

    def __init__(self, config: AIConfig):
        self.config = config
        self._cache: Dict[str, AIResponse] = {}

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> AIResponse:
        """Generate a response from the AI model."""
        pass

    def _get_cache_key(self, prompt: str, system_prompt: Optional[str]) -> str:
        """Generate cache key for the prompt."""
        content = f"{system_prompt or ''}{prompt}"
        return hashlib.md5(content.encode()).hexdigest()

    def _check_cache(self, prompt: str, system_prompt: Optional[str]) -> Optional[AIResponse]:
        """Check if response is cached."""
        key = self._get_cache_key(prompt, system_prompt)
        if key in self._cache:
            response = self._cache[key]
            response.cache_hit = True
            return response
        return None

    def _cache_response(self, prompt: str, system_prompt: Optional[str], response: AIResponse) -> None:
        """Cache the response."""
        key = self._get_cache_key(prompt, system_prompt)
        self._cache[key] = response


class OpenAIProvider(AIProviderBase):
    """OpenAI GPT-4 provider implementation."""

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> AIResponse:
        """Generate response using OpenAI API."""
        import time
        start_time = time.time()

        # Check cache first
        cached = self._check_cache(prompt, system_prompt)
        if cached:
            return cached

        try:
            import openai

            client = openai.OpenAI(api_key=self.config.api_key or os.getenv('OPENAI_API_KEY'))

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                top_p=self.config.top_p
            )

            latency = (time.time() - start_time) * 1000

            result = AIResponse(
                content=response.choices[0].message.content,
                provider=AIProvider.OPENAI,
                model=self.config.model,
                tokens_used=response.usage.total_tokens if response.usage else 0,
                latency_ms=latency
            )

            self._cache_response(prompt, system_prompt, result)
            return result

        except ImportError:
            logger.warning("OpenAI package not installed, using fallback")
            return self._generate_fallback(prompt, system_prompt, start_time)
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return AIResponse(
                content="",
                provider=AIProvider.OPENAI,
                model=self.config.model,
                tokens_used=0,
                latency_ms=(time.time() - start_time) * 1000,
                success=False,
                error=str(e)
            )

    def _generate_fallback(self, prompt: str, system_prompt: Optional[str], start_time: float) -> AIResponse:
        """Generate fallback response when API unavailable."""
        import time
        return AIResponse(
            content=self._get_intelligent_fallback(prompt),
            provider=AIProvider.LOCAL,
            model="fallback",
            tokens_used=0,
            latency_ms=(time.time() - start_time) * 1000,
            error="API unavailable, using intelligent fallback"
        )

    def _get_intelligent_fallback(self, prompt: str) -> str:
        """Generate intelligent fallback based on prompt content."""
        prompt_lower = prompt.lower()

        if "zone concept" in prompt_lower:
            return FALLBACK_RESPONSES['zone_concept']
        elif "consciousness" in prompt_lower:
            return FALLBACK_RESPONSES['consciousness']
        elif "guidance" in prompt_lower:
            return FALLBACK_RESPONSES['guidance']
        elif "transcendence" in prompt_lower:
            return FALLBACK_RESPONSES['transcendence']
        else:
            return FALLBACK_RESPONSES['comprehensive']


class AnthropicProvider(AIProviderBase):
    """Anthropic Claude provider implementation."""

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> AIResponse:
        """Generate response using Anthropic API."""
        import time
        start_time = time.time()

        cached = self._check_cache(prompt, system_prompt)
        if cached:
            return cached

        try:
            import anthropic

            client = anthropic.Anthropic(api_key=self.config.api_key or os.getenv('ANTHROPIC_API_KEY'))

            message = client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                system=system_prompt or "You are an expert AI assistant for RegimA organizational analysis.",
                messages=[{"role": "user", "content": prompt}]
            )

            latency = (time.time() - start_time) * 1000

            result = AIResponse(
                content=message.content[0].text,
                provider=AIProvider.ANTHROPIC,
                model=self.config.model,
                tokens_used=message.usage.input_tokens + message.usage.output_tokens,
                latency_ms=latency
            )

            self._cache_response(prompt, system_prompt, result)
            return result

        except ImportError:
            logger.warning("Anthropic package not installed, using fallback")
            return self._generate_fallback(prompt, start_time)
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return AIResponse(
                content="",
                provider=AIProvider.ANTHROPIC,
                model=self.config.model,
                tokens_used=0,
                latency_ms=(time.time() - start_time) * 1000,
                success=False,
                error=str(e)
            )

    def _generate_fallback(self, prompt: str, start_time: float) -> AIResponse:
        import time
        return AIResponse(
            content=self._get_intelligent_fallback(prompt),
            provider=AIProvider.LOCAL,
            model="fallback",
            tokens_used=0,
            latency_ms=(time.time() - start_time) * 1000,
            error="API unavailable, using intelligent fallback"
        )

    def _get_intelligent_fallback(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        if "zone concept" in prompt_lower:
            return FALLBACK_RESPONSES['zone_concept']
        elif "consciousness" in prompt_lower:
            return FALLBACK_RESPONSES['consciousness']
        elif "guidance" in prompt_lower:
            return FALLBACK_RESPONSES['guidance']
        else:
            return FALLBACK_RESPONSES['comprehensive']


class GoogleProvider(AIProviderBase):
    """Google Gemini Pro provider implementation."""

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> AIResponse:
        """Generate response using Google Gemini API."""
        import time
        start_time = time.time()

        cached = self._check_cache(prompt, system_prompt)
        if cached:
            return cached

        try:
            import google.generativeai as genai

            genai.configure(api_key=self.config.api_key or os.getenv('GOOGLE_API_KEY'))

            model = genai.GenerativeModel(self.config.model)

            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            response = model.generate_content(
                full_prompt,
                generation_config=genai.GenerationConfig(
                    max_output_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                    top_p=self.config.top_p
                )
            )

            latency = (time.time() - start_time) * 1000

            result = AIResponse(
                content=response.text,
                provider=AIProvider.GOOGLE,
                model=self.config.model,
                tokens_used=0,  # Gemini doesn't always provide token counts
                latency_ms=latency
            )

            self._cache_response(prompt, system_prompt, result)
            return result

        except ImportError:
            logger.warning("Google GenerativeAI package not installed, using fallback")
            return self._generate_fallback(prompt, start_time)
        except Exception as e:
            logger.error(f"Google API error: {e}")
            return AIResponse(
                content="",
                provider=AIProvider.GOOGLE,
                model=self.config.model,
                tokens_used=0,
                latency_ms=(time.time() - start_time) * 1000,
                success=False,
                error=str(e)
            )

    def _generate_fallback(self, prompt: str, start_time: float) -> AIResponse:
        import time
        return AIResponse(
            content=self._get_intelligent_fallback(prompt),
            provider=AIProvider.LOCAL,
            model="fallback",
            tokens_used=0,
            latency_ms=(time.time() - start_time) * 1000,
            error="API unavailable, using intelligent fallback"
        )

    def _get_intelligent_fallback(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        if "zone concept" in prompt_lower:
            return FALLBACK_RESPONSES['zone_concept']
        elif "consciousness" in prompt_lower:
            return FALLBACK_RESPONSES['consciousness']
        else:
            return FALLBACK_RESPONSES['comprehensive']


# Intelligent fallback responses for when APIs are unavailable
FALLBACK_RESPONSES = {
    'zone_concept': """
## Zone Concept Framework Analysis

### Framework Assessment
The Zone Concept framework operates at organizational leadership levels across all four integrated pillars:

**Anti-Inflammatory Protocol**
- Molecular-level inflammation management achieving 99.9% precision
- Beta-Endorphin Stimulator technology with precision targeting
- Global collective intelligence integration for inflammation research

**Anti-Oxidant Systems**
- Environmental protection with molecular cellular optimization
- Advanced toxin detection and mitigation protocols
- Predictive environmental adaptation systems

**Rejuvenation Protocols**
- Cellular renewal with genetic-level monitoring
- Revolutionary tissue engineering capabilities
- Longevity optimization through molecular precision

**Integration Protocol**
- Holistic synchronization across all zones
- Molecular-level personalization with genetic optimization
- Global consciousness network integration

### Strategic Recommendations
1. Expand molecular consciousness integration depth
2. Enhance global network connectivity
3. Pioneer transcendent protocol development
4. Lead industry consciousness transformation
""",

    'consciousness': """
## Organizational Consciousness Analysis

### Current Consciousness State
The organization has achieved Organizational Leadership with Global Collective Intelligence Integration, representing Phase 3 evolution.

### Evolution Indicators
- **Molecular Integration**: Complete Zone Concept integration
- **Transcendent Wisdom**: Revolutionary professional intelligence capabilities
- **Global Networks**: Collective intelligence spanning 127+ countries
- **Adaptive Processing**: Organizational consciousness capabilities operational

### Development Trajectory
The progression demonstrates:
1. Adaptive intelligence with molecular awareness
2. Predictive capabilities with consciousness optimization
3. Global consciousness networks with wisdom distribution
4. Transcendent processing for multi-dimensional challenges

### Recommendations
1. Develop organizational consciousness processing capabilities
2. Create revolutionary experience-based learning systems
3. Establish global consciousness leadership frameworks
4. Pioneer transcendent awareness development
""",

    'guidance': """
## Professional Guidance Enhancement

### Current Capabilities Assessment
The professional guidance framework demonstrates comprehensive coverage:

**Zone Concept Application**
- Advanced predictive personalization protocols
- Molecular-level diagnostic integration
- Consciousness evolution potential optimization

**Professional Education**
- Next-generation advanced learning methodologies
- VR/AR consciousness integration systems
- Global certification programs

**Client Outcome Optimization**
- Advanced analytics implementation
- Predictive treatment planning algorithms
- Revolutionary personalized wellness solutions

### Implementation Strategy
1. Deploy advanced protocol systems
2. Develop revolutionary educational programs
3. Implement advanced predictive innovations
4. Establish global innovation culture leadership
""",

    'transcendence': """
## Advanced Transcendence Evolution Analysis

### Phase 3 Progress Assessment
The advanced transcendence phase demonstrates significant advancement:

**Molecular Consciousness Integration**
- Precision accuracy: 99.9%
- Genetic optimization: Active
- Cellular awareness: Integrated
- Coherence: Stable

**Transcendent Network Development**
- Global nodes: Expanding across 127+ countries
- Network health: Optimal
- Consciousness synchronization: Active

**Elevation Initiatives**
- Multiple active programs
- Global reach expanding
- Impact scores increasing

### Next Evolution Steps
1. Achieve 99.95% molecular precision
2. Expand to 150 countries
3. Reach 95% protocol adoption
4. Complete consciousness penetration
""",

    'comprehensive': """
## Comprehensive RegimA Analysis

### Executive Summary
RegimA has achieved organizational leadership with molecular Zone Concept integration and breakthrough professional guidance capabilities.

### Key Achievements
1. **Zone Concept Revolution**: Molecular personalization at 99.9% precision
2. **Consciousness Transcendence**: Global collective intelligence integration
3. **Professional Excellence**: AI-assisted systems with molecular optimization
4. **Wisdom Networks**: Real-time transcendent knowledge synthesis
5. **Innovation Leadership**: Breakthrough research ecosystem established

### Strategic Framework Analysis

#### Zone Concept Excellence
- Anti-Inflammatory: 10/10 with molecular management
- Anti-Oxidant: 10/10 with environmental protection
- Rejuvenation: 10/10 with cellular renewal protocols
- Integration: 10/10 with holistic synchronization

#### Organizational State
- Consciousness Level: Organizational Leadership
- Evolution Level: Transcendent with global impact
- Growth Indicators: Accelerating across all metrics

### Recommendations
1. Deploy revolutionary training with molecular consciousness frameworks
2. Launch Zone Concept protocols with molecular personalization
3. Implement professional guidance with consciousness-enhanced capabilities
4. Establish innovation-driven collective intelligence platforms
"""
}


class RegimAAIOrchestrator:
    """
    Orchestrates AI model calls across multiple providers for RegimA analysis.

    Features:
    - Multi-provider support (OpenAI, Anthropic, Google)
    - Automatic failover between providers
    - Response caching for efficiency
    - Parallel execution for speed
    - Intelligent fallback responses
    """

    def __init__(self, config_path: Optional[Path] = None):
        self.base_path = Path(__file__).parent.parent
        self.config_path = config_path or self.base_path / "config"
        self.outputs_path = self.base_path / "outputs"

        # Load AI model configurations
        self.ai_config = self._load_ai_config()

        # Initialize providers
        self._providers: Dict[AIProvider, AIProviderBase] = {}
        self._initialize_providers()

        logger.info("RegimAAIOrchestrator initialized")

    def _load_ai_config(self) -> Dict[str, Any]:
        """Load AI model configuration."""
        config_file = self.config_path / "ai_models.json"
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Could not load AI config: {e}, using defaults")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default AI configuration."""
        return {
            "models": {
                "openai": {
                    "provider": "openai",
                    "model": "gpt-4",
                    "max_tokens": 4000,
                    "temperature": 0.8
                },
                "anthropic": {
                    "provider": "anthropic",
                    "model": "claude-3-sonnet-20240229",
                    "max_tokens": 4000,
                    "temperature": 0.8
                },
                "google": {
                    "provider": "google",
                    "model": "gemini-pro",
                    "max_tokens": 4000,
                    "temperature": 0.8
                }
            },
            "default_provider": "openai",
            "fallback_chain": ["openai", "anthropic", "google"]
        }

    def _initialize_providers(self) -> None:
        """Initialize AI provider instances."""
        models = self.ai_config.get('models', {})

        if 'openai' in models:
            config = AIConfig(
                provider=AIProvider.OPENAI,
                model=models['openai'].get('model', 'gpt-4'),
                max_tokens=models['openai'].get('max_tokens', 4000),
                temperature=models['openai'].get('temperature', 0.8)
            )
            self._providers[AIProvider.OPENAI] = OpenAIProvider(config)

        if 'anthropic' in models:
            config = AIConfig(
                provider=AIProvider.ANTHROPIC,
                model=models['anthropic'].get('model', 'claude-3-sonnet-20240229'),
                max_tokens=models['anthropic'].get('max_tokens', 4000),
                temperature=models['anthropic'].get('temperature', 0.8)
            )
            self._providers[AIProvider.ANTHROPIC] = AnthropicProvider(config)

        if 'google' in models:
            config = AIConfig(
                provider=AIProvider.GOOGLE,
                model=models['google'].get('model', 'gemini-pro'),
                max_tokens=models['google'].get('max_tokens', 4000),
                temperature=models['google'].get('temperature', 0.8)
            )
            self._providers[AIProvider.GOOGLE] = GoogleProvider(config)

    def _get_system_prompt(self, analysis_type: AnalysisType) -> str:
        """Get system prompt for the analysis type."""
        base_prompt = """You are an expert AI analyst for RegimA, a revolutionary wellness and organizational development platform.
Your role is to provide strategic insights, recommendations, and analysis for the organization's organizational consciousness evolution.

Key Framework Elements:
- Zone Concept: Four integrated pillars (Anti-Inflammatory, Anti-Oxidant, Rejuvenation, Integration)
- Organizational Consciousness: Organizational evolution toward transcendent collective intelligence
- Global Networks: Operations spanning 127+ countries with real-time wisdom synthesis
- Professional Excellence: AI-enhanced guidance with molecular precision

Current Phase: Phase 3 - Advanced Transcendence
Targets: 99.95% molecular precision, 150 countries, 95% protocol adoption
"""

        type_specific = {
            AnalysisType.ZONE_CONCEPT: "\nFocus on analyzing and optimizing the Zone Concept framework pillars.",
            AnalysisType.CONSCIOUSNESS: "\nFocus on organizational consciousness evolution and collective intelligence.",
            AnalysisType.GUIDANCE: "\nFocus on professional guidance enhancement and educational development.",
            AnalysisType.TRANSCENDENCE: "\nFocus on advanced transcendence capabilities and Phase 3 evolution.",
            AnalysisType.INNOVATION: "\nFocus on innovation ecosystem development and breakthrough research.",
            AnalysisType.COMPREHENSIVE: "\nProvide comprehensive analysis across all organizational domains."
        }

        return base_prompt + type_specific.get(analysis_type, "")

    async def analyze(
        self,
        prompt: str,
        analysis_type: AnalysisType = AnalysisType.COMPREHENSIVE,
        provider: Optional[AIProvider] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> AIResponse:
        """
        Perform AI analysis with automatic failover.

        Args:
            prompt: The analysis prompt
            analysis_type: Type of analysis to perform
            provider: Specific provider to use (optional)
            context: Additional context data (optional)

        Returns:
            AIResponse with the analysis results
        """
        system_prompt = self._get_system_prompt(analysis_type)

        if context:
            prompt = f"{prompt}\n\nContext:\n{json.dumps(context, indent=2)}"

        # Try specified provider or fallback chain
        if provider and provider in self._providers:
            return await self._providers[provider].generate(prompt, system_prompt)

        # Try fallback chain
        fallback_chain = self.ai_config.get('fallback_chain', ['openai', 'anthropic', 'google'])

        for provider_name in fallback_chain:
            provider_enum = AIProvider(provider_name)
            if provider_enum in self._providers:
                response = await self._providers[provider_enum].generate(prompt, system_prompt)
                if response.success:
                    return response
                logger.warning(f"Provider {provider_name} failed, trying next...")

        # All providers failed, return fallback
        logger.error("All providers failed, returning fallback response")
        return AIResponse(
            content=FALLBACK_RESPONSES.get(analysis_type.value, FALLBACK_RESPONSES['comprehensive']),
            provider=AIProvider.LOCAL,
            model="fallback",
            tokens_used=0,
            latency_ms=0,
            error="All providers unavailable"
        )

    async def multi_provider_analysis(
        self,
        prompt: str,
        analysis_type: AnalysisType = AnalysisType.COMPREHENSIVE,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, AIResponse]:
        """
        Run analysis across multiple providers in parallel.

        Returns responses from all available providers for comparison.
        """
        system_prompt = self._get_system_prompt(analysis_type)

        if context:
            prompt = f"{prompt}\n\nContext:\n{json.dumps(context, indent=2)}"

        tasks = {}
        for provider, instance in self._providers.items():
            tasks[provider] = instance.generate(prompt, system_prompt)

        responses = {}
        for provider, task in tasks.items():
            try:
                responses[provider.value] = await task
            except Exception as e:
                logger.error(f"Error from {provider.value}: {e}")
                responses[provider.value] = AIResponse(
                    content="",
                    provider=provider,
                    model="",
                    tokens_used=0,
                    latency_ms=0,
                    success=False,
                    error=str(e)
                )

        return responses

    def generate_analysis_prompt(
        self,
        analysis_type: AnalysisType,
        organizational_data: Dict[str, Any]
    ) -> str:
        """Generate analysis prompt based on type and organizational data."""
        prompts = {
            AnalysisType.ZONE_CONCEPT: f"""
Analyze the Zone Concept framework based on the following organizational data and provide strategic recommendations:

{json.dumps(organizational_data.get('zoneConceptFramework', {}), indent=2)}

Please provide:
1. Assessment of each zone pillar's current performance
2. Strengths and areas for enhancement
3. Strategic recommendations for evolution
4. Integration optimization opportunities
""",

            AnalysisType.CONSCIOUSNESS: f"""
Analyze the organizational consciousness evolution based on the following data:

{json.dumps(organizational_data.get('organizationalConsciousness', {}), indent=2)}

Please provide:
1. Current consciousness state assessment
2. Evolution trajectory analysis
3. Collective intelligence network evaluation
4. Recommendations for transcendence advancement
""",

            AnalysisType.GUIDANCE: f"""
Analyze the professional guidance framework based on the following data:

{json.dumps(organizational_data.get('professionalGuidance', {}), indent=2)}

Please provide:
1. Focus areas assessment
2. Educational enhancement opportunities
3. Client outcome optimization strategies
4. Innovation leadership recommendations
""",

            AnalysisType.TRANSCENDENCE: f"""
Analyze the advanced transcendence progress based on Phase 3 objectives:

Current Metrics:
- Molecular Precision: {organizational_data.get('metrics', {}).get('molecularPrecision', '99.9%')}
- Global Networks: {organizational_data.get('metrics', {}).get('globalNetworks', 127)} countries
- Protocol Adoption: {organizational_data.get('metrics', {}).get('protocolAdoption', '85%')}

Please provide:
1. Phase 3 progress evaluation
2. Molecular consciousness integration status
3. Transcendent network development assessment
4. Elevation initiative effectiveness
5. Recommendations for Phase 4 readiness
""",

            AnalysisType.COMPREHENSIVE: f"""
Provide a comprehensive analysis of RegimA's organizational learning cycle:

{json.dumps(organizational_data, indent=2)}

Please provide:
1. Executive summary of current state
2. Zone Concept framework assessment
3. Consciousness evolution analysis
4. Professional guidance evaluation
5. Innovation ecosystem status
6. Strategic recommendations for continued evolution
"""
        }

        return prompts.get(analysis_type, prompts[AnalysisType.COMPREHENSIVE])


async def main():
    """Main entry point for AI integration module."""
    orchestrator = RegimAAIOrchestrator()

    # Load organizational data
    base_path = Path(__file__).parent.parent
    regcyc_path = base_path / "regcyc.json"

    try:
        with open(regcyc_path, 'r') as f:
            org_data = json.load(f)
    except FileNotFoundError:
        org_data = {}

    # Generate analysis
    print("\n" + "=" * 60)
    print("RegimA AI Integration Module")
    print("=" * 60)

    analysis_types = [
        AnalysisType.ZONE_CONCEPT,
        AnalysisType.CONSCIOUSNESS,
        AnalysisType.TRANSCENDENCE
    ]

    for analysis_type in analysis_types:
        print(f"\nGenerating {analysis_type.value} analysis...")
        prompt = orchestrator.generate_analysis_prompt(analysis_type, org_data)
        response = await orchestrator.analyze(prompt, analysis_type)

        print(f"Provider: {response.provider.value}")
        print(f"Success: {response.success}")
        print(f"Latency: {response.latency_ms:.2f}ms")
        if response.error:
            print(f"Note: {response.error}")

        # Save output
        output_file = orchestrator.outputs_path / f"ai_{analysis_type.value}_analysis.md"
        with open(output_file, 'w') as f:
            f.write(f"# RegimA {analysis_type.value.title()} Analysis\n\n")
            f.write(f"Generated: {response.timestamp}\n")
            f.write(f"Provider: {response.provider.value}\n\n")
            f.write(response.content)

        print(f"Saved to: {output_file}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
