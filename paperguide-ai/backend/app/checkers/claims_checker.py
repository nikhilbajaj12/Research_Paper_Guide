"""Claims integrity checker for detecting numeric claims."""

import re
from typing import List, Dict
from ..core import get_logger

logger = get_logger(__name__)

PERCENTAGE_PATTERN = r'(\d+\.?\d*)\s*%'
DECIMAL_PATTERN = r'\b0\.\d+\b'
SPEEDUP_PATTERN = r'(\d+\.?\d*)\s*x(?:times)?|(\d+\.?\d*)×'
BENCHMARK_KEYWORDS = [
    'accuracy', 'loss', 'perplexity', 'speedup', 'throughput',
    'latency', 'improvement', 'outperforms', 'state-of-the-art',
    'achieves', 'metric', 'benchmark', 'baseline', 'performance'
]


class ClaimsChecker:
    """Check for numeric claims that need verification."""

    def check(self, extracted_text: str, parsed_paper: Dict) -> List[Dict]:
        """Check for unverified numeric claims."""
        logger.info("Checking for numeric claims that need verification")
        issues = []
        
        if not extracted_text:
            return issues
        
        text_lower = extracted_text.lower()
        
        percentages = re.findall(PERCENTAGE_PATTERN, extracted_text)
        if percentages:
            for percentage in percentages:
                context_start = extracted_text.lower().find(percentage + '%')
                if context_start > 0:
                    context = extracted_text[max(0, context_start - 50):min(len(extracted_text), context_start + 100)]
                    context = context.replace('\n', ' ')[:150]
                    
                    issues.append({
                        "issue_id": f"claim_percentage_{len(issues)}",
                        "category": "claims_integrity",
                        "severity": "warning",
                        "message": f"Numeric claim detected: {percentage}%",
                        "location": f"Context: {context}",
                        "suggested_fix": "Verify this numeric claim using experiment logs, tables, or citations. If not verified, remove or mark as pending validation.",
                        "needs_verification": True,
                    })
        
        decimals = re.findall(DECIMAL_PATTERN, extracted_text)
        if decimals:
            for decimal in set(decimals):
                context_start = extracted_text.find(decimal)
                if context_start > 0:
                    context = extracted_text[max(0, context_start - 50):min(len(extracted_text), context_start + 100)]
                    context = context.replace('\n', ' ')[:150]
                    
                    in_benchmark_context = any(
                        keyword in text_lower[max(0, context_start - 100):min(len(text_lower), context_start + 100)]
                        for keyword in BENCHMARK_KEYWORDS
                    )
                    
                    if in_benchmark_context:
                        issues.append({
                            "issue_id": f"claim_decimal_{len(issues)}",
                            "category": "claims_integrity",
                            "severity": "warning",
                            "message": f"Numeric metric detected: {decimal}",
                            "location": f"Context: {context}",
                            "suggested_fix": "Verify this numeric claim using experiment logs, tables, or citations. If not verified, remove or mark as pending validation.",
                            "needs_verification": True,
                        })
        
        speedups = re.findall(SPEEDUP_PATTERN, extracted_text)
        if speedups:
            for speedup_tuple in speedups:
                speedup = speedup_tuple[0] if speedup_tuple[0] else speedup_tuple[1]
                if speedup:
                    context_start = extracted_text.lower().find(speedup.lower())
                    if context_start > 0:
                        context = extracted_text[max(0, context_start - 50):min(len(extracted_text), context_start + 100)]
                        context = context.replace('\n', ' ')[:150]
                        
                        issues.append({
                            "issue_id": f"claim_speedup_{len(issues)}",
                            "category": "claims_integrity",
                            "severity": "warning",
                            "message": f"Speedup claim detected: {speedup}x",
                            "location": f"Context: {context}",
                            "suggested_fix": "Verify this numeric claim using experiment logs, tables, or citations. If not verified, remove or mark as pending validation.",
                            "needs_verification": True,
                        })
        
        return issues
