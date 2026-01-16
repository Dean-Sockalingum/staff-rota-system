"""
PDSA Data Analyzer
Statistical analysis of cycle data using ML techniques
"""

import numpy as np
from scipy import stats
from typing import List, Dict, Tuple, Optional
from datetime import datetime


class PDSADataAnalyzer:
    """
    Analyze PDSA cycle data for trends, statistical significance, and control limits.
    Uses statistical ML techniques for automated insights.
    """
    
    def analyze_cycle_data(
        self,
        datapoints: List[Dict[str, any]],
        baseline_mean: Optional[float] = None,
        target_value: Optional[float] = None
    ) -> Dict[str, any]:
        """
        Comprehensive analysis of PDSA cycle data.
        
        Args:
            datapoints: List of dicts with 'date', 'value', 'notes'
            baseline_mean: Pre-intervention baseline mean
            target_value: Target value for the metric
            
        Returns:
            Dictionary with:
                - trend: 'improving', 'worsening', 'stable'
                - statistical_significance: p-value from Mann-Kendall test
                - control_limits: UCL, LCL, centerline
                - insights: List of automated insights
                - recommendations: Actionable next steps
                - chart_config: Configuration for Chart.js visualization
        """
        if not datapoints or len(datapoints) < 3:
            return self._insufficient_data_response()
        
        # Extract values and dates
        values = [dp['value'] for dp in datapoints]
        dates = [dp.get('date', datetime.now()) for dp in datapoints]
        
        # Sort by date
        sorted_data = sorted(zip(dates, values), key=lambda x: x[0])
        sorted_values = [v for _, v in sorted_data]
        sorted_dates = [d for d, _ in sorted_data]
        
        # Calculate trend
        trend_result = self._mann_kendall_test(sorted_values)
        
        # Calculate control limits
        control_limits = self._calculate_control_limits(sorted_values)
        
        # Check for special cause variation
        special_causes = self._detect_special_causes(
            sorted_values,
            control_limits['ucl'],
            control_limits['lcl'],
            control_limits['centerline']
        )
        
        # Generate insights
        insights = self._generate_insights(
            sorted_values,
            trend_result,
            control_limits,
            special_causes,
            baseline_mean,
            target_value
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            trend_result,
            special_causes,
            sorted_values,
            target_value
        )
        
        # Build Chart.js configuration
        chart_config = self._build_chart_config(
            sorted_dates,
            sorted_values,
            control_limits,
            baseline_mean,
            target_value
        )
        
        return {
            'trend': trend_result['trend'],
            'trend_strength': trend_result['tau'],
            'statistical_significance': trend_result['p_value'],
            'is_significant': trend_result['p_value'] < 0.05,
            'control_limits': control_limits,
            'special_causes': special_causes,
            'insights': insights,
            'recommendations': recommendations,
            'chart_config': chart_config,
            'summary_stats': {
                'mean': np.mean(sorted_values),
                'median': np.median(sorted_values),
                'std_dev': np.std(sorted_values),
                'min': min(sorted_values),
                'max': max(sorted_values),
                'n_points': len(sorted_values)
            }
        }
    
    def _mann_kendall_test(self, data: List[float]) -> Dict[str, any]:
        """
        Mann-Kendall trend test - non-parametric test for monotonic trend.
        More robust than linear regression for small samples.
        """
        n = len(data)
        
        # Calculate S statistic
        s = 0
        for i in range(n - 1):
            for j in range(i + 1, n):
                s += np.sign(data[j] - data[i])
        
        # Calculate variance
        var_s = n * (n - 1) * (2 * n + 5) / 18
        
        # Calculate Z score
        if s > 0:
            z = (s - 1) / np.sqrt(var_s)
        elif s < 0:
            z = (s + 1) / np.sqrt(var_s)
        else:
            z = 0
        
        # Calculate p-value (two-tailed)
        p_value = 2 * (1 - stats.norm.cdf(abs(z)))
        
        # Calculate Kendall's tau (correlation coefficient)
        tau = s / (0.5 * n * (n - 1))
        
        # Determine trend
        if p_value < 0.05:
            if tau > 0:
                trend = 'improving' if data[-1] > data[0] else 'worsening'
            else:
                trend = 'improving' if data[-1] < data[0] else 'worsening'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            's_statistic': s,
            'tau': round(tau, 3),
            'z_score': round(z, 3),
            'p_value': round(p_value, 4)
        }
    
    def _calculate_control_limits(self, data: List[float]) -> Dict[str, float]:
        """
        Calculate control chart limits (UCL, LCL, centerline).
        Uses 3-sigma limits for individual measurements (I-chart).
        """
        # Centerline (mean)
        centerline = np.mean(data)
        
        # Calculate moving range
        moving_ranges = [abs(data[i] - data[i-1]) for i in range(1, len(data))]
        avg_moving_range = np.mean(moving_ranges) if moving_ranges else 0
        
        # Control limits using moving range method
        # For individuals chart: limits = mean ± 2.66 * avg_moving_range
        d2 = 1.128  # constant for n=2
        sigma = avg_moving_range / d2
        
        ucl = centerline + (3 * sigma)
        lcl = centerline - (3 * sigma)
        
        # LCL can't be negative for count data
        if lcl < 0 and all(v >= 0 for v in data):
            lcl = 0
        
        return {
            'ucl': round(ucl, 2),
            'lcl': round(lcl, 2),
            'centerline': round(centerline, 2),
            'sigma': round(sigma, 2)
        }
    
    def _detect_special_causes(
        self,
        data: List[float],
        ucl: float,
        lcl: float,
        centerline: float
    ) -> List[Dict[str, any]]:
        """
        Detect special cause variation using Western Electric rules.
        """
        special_causes = []
        
        # Rule 1: Point outside control limits
        for i, value in enumerate(data):
            if value > ucl:
                special_causes.append({
                    'rule': 'Point above UCL',
                    'index': i,
                    'value': value,
                    'severity': 'high'
                })
            elif value < lcl:
                special_causes.append({
                    'rule': 'Point below LCL',
                    'index': i,
                    'value': value,
                    'severity': 'high'
                })
        
        # Rule 2: 8 consecutive points on one side of centerline
        if len(data) >= 8:
            for i in range(len(data) - 7):
                segment = data[i:i+8]
                if all(v > centerline for v in segment):
                    special_causes.append({
                        'rule': '8 consecutive points above centerline',
                        'index': i,
                        'severity': 'medium'
                    })
                elif all(v < centerline for v in segment):
                    special_causes.append({
                        'rule': '8 consecutive points below centerline',
                        'index': i,
                        'severity': 'medium'
                    })
        
        # Rule 3: 6 consecutive increasing or decreasing points
        if len(data) >= 6:
            for i in range(len(data) - 5):
                segment = data[i:i+6]
                if all(segment[j] < segment[j+1] for j in range(5)):
                    special_causes.append({
                        'rule': '6 consecutive increasing points (trend)',
                        'index': i,
                        'severity': 'medium'
                    })
                elif all(segment[j] > segment[j+1] for j in range(5)):
                    special_causes.append({
                        'rule': '6 consecutive decreasing points (trend)',
                        'index': i,
                        'severity': 'medium'
                    })
        
        return special_causes
    
    def _generate_insights(
        self,
        data: List[float],
        trend_result: Dict,
        control_limits: Dict,
        special_causes: List[Dict],
        baseline: Optional[float],
        target: Optional[float]
    ) -> List[str]:
        """Generate automated insights from the analysis"""
        insights = []
        
        # Trend insights
        if trend_result['trend'] != 'stable':
            confidence = 'significant' if trend_result['p_value'] < 0.05 else 'possible'
            insights.append(
                f"Data shows {confidence} {trend_result['trend']} trend "
                f"(p={trend_result['p_value']:.4f})"
            )
        
        # Special cause insights
        if special_causes:
            high_severity = [sc for sc in special_causes if sc.get('severity') == 'high']
            if high_severity:
                insights.append(
                    f"⚠️ {len(high_severity)} point(s) outside control limits - "
                    f"indicates special cause variation requiring investigation"
                )
        
        # Baseline comparison
        if baseline is not None:
            current_mean = np.mean(data)
            change = ((current_mean - baseline) / baseline) * 100
            direction = 'improvement' if change > 0 else 'decline'
            insights.append(
                f"Current mean ({current_mean:.2f}) represents {abs(change):.1f}% "
                f"{direction} from baseline ({baseline:.2f})"
            )
        
        # Target progress
        if target is not None:
            current_mean = np.mean(data)
            if abs(current_mean - target) / target < 0.1:  # Within 10%
                insights.append(f"✅ Currently within 10% of target ({target})")
            else:
                gap = abs(target - current_mean)
                insights.append(f"Gap to target: {gap:.2f} units remaining")
        
        # Variation insight
        cv = (control_limits['sigma'] / control_limits['centerline']) * 100
        if cv < 10:
            insights.append("Process shows low variation (CV < 10%) - good stability")
        elif cv > 30:
            insights.append("Process shows high variation (CV > 30%) - investigate causes")
        
        return insights
    
    def _generate_recommendations(
        self,
        trend_result: Dict,
        special_causes: List[Dict],
        data: List[float],
        target: Optional[float]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if special_causes:
            recommendations.append(
                "Investigate special causes: Review data points outside control limits "
                "for assignable causes"
            )
        
        if trend_result['trend'] == 'improving':
            recommendations.append(
                "Positive trend detected - standardize current practices and consider "
                "spreading to other areas"
            )
        elif trend_result['trend'] == 'worsening':
            recommendations.append(
                "Negative trend detected - review recent changes and consider PDSA "
                "cycle to address decline"
            )
        
        if trend_result['trend'] == 'stable' and not special_causes:
            recommendations.append(
                "Process is stable but may need different intervention for improvement - "
                "consider new change ideas"
            )
        
        if target is not None:
            current_mean = np.mean(data)
            if current_mean >= target * 0.9:  # Within 90% of target
                recommendations.append(
                    "Close to target - maintain current interventions and monitor sustainability"
                )
        
        return recommendations
    
    def _build_chart_config(
        self,
        dates: List[datetime],
        values: List[float],
        control_limits: Dict,
        baseline: Optional[float],
        target: Optional[float]
    ) -> Dict:
        """Build Chart.js configuration for visualization"""
        return {
            'type': 'line',
            'data': {
                'labels': [d.strftime('%Y-%m-%d') if isinstance(d, datetime) else str(d) 
                          for d in dates],
                'datasets': [
                    {
                        'label': 'Measurement',
                        'data': values,
                        'borderColor': 'rgb(75, 192, 192)',
                        'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                        'tension': 0.1
                    },
                    {
                        'label': 'UCL',
                        'data': [control_limits['ucl']] * len(values),
                        'borderColor': 'rgb(255, 99, 132)',
                        'borderDash': [5, 5],
                        'fill': False
                    },
                    {
                        'label': 'Centerline',
                        'data': [control_limits['centerline']] * len(values),
                        'borderColor': 'rgb(54, 162, 235)',
                        'borderDash': [5, 5],
                        'fill': False
                    },
                    {
                        'label': 'LCL',
                        'data': [control_limits['lcl']] * len(values),
                        'borderColor': 'rgb(255, 99, 132)',
                        'borderDash': [5, 5],
                        'fill': False
                    }
                ]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'PDSA Run Chart with Control Limits'
                    },
                    'legend': {
                        'display': True
                    }
                },
                'scales': {
                    'y': {
                        'beginAtZero': False
                    }
                }
            }
        }
    
    def _insufficient_data_response(self) -> Dict:
        """Return when insufficient data for analysis"""
        return {
            'trend': 'insufficient_data',
            'insights': ['Need at least 3 data points for statistical analysis'],
            'recommendations': ['Continue collecting data points for meaningful analysis'],
            'chart_config': None
        }
