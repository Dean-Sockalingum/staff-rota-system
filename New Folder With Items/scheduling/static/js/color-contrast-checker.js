/**
 * Color Contrast Checker - WCAG 2.1 Compliance Utility
 * Staff Rota System - December 2025
 * 
 * This utility helps ensure all text/background color combinations
 * meet WCAG 2.1 accessibility standards for color contrast.
 * 
 * Standards:
 * - WCAG AA Normal Text: 4.5:1 contrast ratio
 * - WCAG AA Large Text (18pt+): 3:1 contrast ratio
 * - WCAG AAA Normal Text: 7:1 contrast ratio
 * - WCAG AAA Large Text: 4.5:1 contrast ratio
 */

const ColorContrastChecker = {
    /**
     * Calculate relative luminance of a color
     * @param {string} color - Hex color (e.g., '#FF0000') or RGB string
     * @returns {number} Relative luminance (0-1)
     */
    getLuminance(color) {
        // Convert hex to RGB
        let r, g, b;
        
        if (color.startsWith('#')) {
            const hex = color.replace('#', '');
            r = parseInt(hex.substr(0, 2), 16) / 255;
            g = parseInt(hex.substr(2, 2), 16) / 255;
            b = parseInt(hex.substr(4, 2), 16) / 255;
        } else if (color.startsWith('rgb')) {
            const matches = color.match(/\d+/g);
            r = parseInt(matches[0]) / 255;
            g = parseInt(matches[1]) / 255;
            b = parseInt(matches[2]) / 255;
        } else {
            console.error('Unsupported color format:', color);
            return 0;
        }
        
        // Apply gamma correction
        const rsRGB = r <= 0.03928 ? r / 12.92 : Math.pow((r + 0.055) / 1.055, 2.4);
        const gsRGB = g <= 0.03928 ? g / 12.92 : Math.pow((g + 0.055) / 1.055, 2.4);
        const bsRGB = b <= 0.03928 ? b / 12.92 : Math.pow((b + 0.055) / 1.055, 2.4);
        
        // Calculate relative luminance
        return 0.2126 * rsRGB + 0.7152 * gsRGB + 0.0722 * bsRGB;
    },
    
    /**
     * Calculate contrast ratio between two colors
     * @param {string} foreground - Foreground color
     * @param {string} background - Background color
     * @returns {number} Contrast ratio (1-21)
     */
    getContrastRatio(foreground, background) {
        const l1 = this.getLuminance(foreground);
        const l2 = this.getLuminance(background);
        
        const lighter = Math.max(l1, l2);
        const darker = Math.min(l1, l2);
        
        return (lighter + 0.05) / (darker + 0.05);
    },
    
    /**
     * Check if color combination meets WCAG standards
     * @param {string} foreground - Foreground color
     * @param {string} background - Background color
     * @param {boolean} isLargeText - Whether text is large (18pt+ or 14pt+ bold)
     * @returns {Object} Compliance results
     */
    checkCompliance(foreground, background, isLargeText = false) {
        const ratio = this.getContrastRatio(foreground, background);
        
        // WCAG thresholds
        const aaThreshold = isLargeText ? 3.0 : 4.5;
        const aaaThreshold = isLargeText ? 4.5 : 7.0;
        
        return {
            ratio: ratio.toFixed(2),
            passAA: ratio >= aaThreshold,
            passAAA: ratio >= aaaThreshold,
            level: ratio >= aaaThreshold ? 'AAA' : ratio >= aaThreshold ? 'AA' : 'Fail',
            recommendation: ratio < aaThreshold ? this.getRecommendation(foreground, background) : null
        };
    },
    
    /**
     * Get recommendation for improving contrast
     * @param {string} foreground - Foreground color
     * @param {string} background - Background color
     * @returns {string} Recommendation
     */
    getRecommendation(foreground, background) {
        const fgLum = this.getLuminance(foreground);
        const bgLum = this.getLuminance(background);
        
        if (fgLum > bgLum) {
            return 'Lighten foreground or darken background';
        } else {
            return 'Darken foreground or lighten background';
        }
    },
    
    /**
     * Audit all text elements on the page
     * @returns {Array} Array of audit results
     */
    auditPage() {
        const results = [];
        const textElements = document.querySelectorAll('p, span, a, button, h1, h2, h3, h4, h5, h6, li, td, th, label, input, select, textarea');
        
        textElements.forEach((element, index) => {
            const computedStyle = window.getComputedStyle(element);
            const foreground = computedStyle.color;
            const background = this.getBackgroundColor(element);
            const fontSize = parseFloat(computedStyle.fontSize);
            const fontWeight = computedStyle.fontWeight;
            
            // Determine if large text (18px+ or 14px+ bold)
            const isLargeText = fontSize >= 18 || (fontSize >= 14 && parseInt(fontWeight) >= 700);
            
            const compliance = this.checkCompliance(foreground, background, isLargeText);
            
            if (!compliance.passAA) {
                results.push({
                    element: element.tagName.toLowerCase(),
                    index: index,
                    text: element.textContent.trim().substring(0, 50),
                    foreground: foreground,
                    background: background,
                    fontSize: fontSize + 'px',
                    isLargeText: isLargeText,
                    ...compliance
                });
            }
        });
        
        return results;
    },
    
    /**
     * Get effective background color (traverses parent elements)
     * @param {Element} element - DOM element
     * @returns {string} Background color
     */
    getBackgroundColor(element) {
        let current = element;
        
        while (current && current !== document.body) {
            const bg = window.getComputedStyle(current).backgroundColor;
            
            // Check if background is not transparent
            if (bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent') {
                return bg;
            }
            
            current = current.parentElement;
        }
        
        // Default to white if no background found
        return 'rgb(255, 255, 255)';
    },
    
    /**
     * Generate contrast report for console
     */
    generateReport() {
        console.group('🎨 Color Contrast Audit Report');
        
        const issues = this.auditPage();
        
        if (issues.length === 0) {
            console.log('✅ All color combinations pass WCAG AA standards!');
        } else {
            console.warn(`⚠️  Found ${issues.length} contrast issues:`);
            
            issues.forEach((issue, index) => {
                console.group(`Issue ${index + 1}: <${issue.element}>`);
                console.log('Text:', issue.text);
                console.log('Foreground:', issue.foreground);
                console.log('Background:', issue.background);
                console.log('Font Size:', issue.fontSize, issue.isLargeText ? '(Large)' : '(Normal)');
                console.log('Contrast Ratio:', issue.ratio + ':1');
                console.log('Level:', issue.level);
                console.log('Recommendation:', issue.recommendation);
                console.groupEnd();
            });
        }
        
        console.groupEnd();
        
        return issues;
    },
    
    /**
     * Test design system color combinations
     */
    testDesignSystemColors() {
        console.group('🎨 Design System Color Contrast Tests');
        
        const colorTests = [
            // Primary on white
            { fg: '#0066FF', bg: '#FFFFFF', name: 'Primary-500 on White' },
            { fg: '#1976D2', bg: '#FFFFFF', name: 'Primary-700 on White' },
            { fg: '#0D47A1', bg: '#FFFFFF', name: 'Primary-900 on White' },
            
            // White on primary
            { fg: '#FFFFFF', bg: '#0066FF', name: 'White on Primary-500' },
            { fg: '#FFFFFF', bg: '#1976D2', name: 'White on Primary-700' },
            { fg: '#FFFFFF', bg: '#0D47A1', name: 'White on Primary-900' },
            
            // Success combinations
            { fg: '#2E7D32', bg: '#FFFFFF', name: 'Success-500 on White' },
            { fg: '#FFFFFF', bg: '#2E7D32', name: 'White on Success-500' },
            { fg: '#FFFFFF', bg: '#388E3C', name: 'White on Success-700' },
            
            // Warning combinations
            { fg: '#E65100', bg: '#FFFFFF', name: 'Warning-500 on White' },
            { fg: '#FFFFFF', bg: '#E65100', name: 'White on Warning-500' },
            { fg: '#000000', bg: '#E65100', name: 'Black on Warning-500' },
            
            // Danger combinations
            { fg: '#C62828', bg: '#FFFFFF', name: 'Danger-500 on White' },
            { fg: '#FFFFFF', bg: '#C62828', name: 'White on Danger-500' },
            { fg: '#FFFFFF', bg: '#D32F2F', name: 'White on Danger-700' },
            
            // Neutral text colors
            { fg: '#1F2933', bg: '#FFFFFF', name: 'Neutral-1000 on White' },
            { fg: '#323F4B', bg: '#FFFFFF', name: 'Neutral-900 on White' },
            { fg: '#616E7C', bg: '#FFFFFF', name: 'Neutral-600 on White' },
            { fg: '#52606D', bg: '#FFFFFF', name: 'Neutral-500 on White' },
            { fg: '#9AA5B1', bg: '#FFFFFF', name: 'Neutral-400 on White' },
            
            // Light backgrounds
            { fg: '#1F2933', bg: '#F5F7FA', name: 'Neutral-1000 on Neutral-100' },
            { fg: '#323F4B', bg: '#FAFBFC', name: 'Neutral-900 on Neutral-50' },
        ];
        
        colorTests.forEach(test => {
            const result = this.checkCompliance(test.fg, test.bg, false);
            const icon = result.passAAA ? '✅ AAA' : result.passAA ? '✔️  AA' : '❌ Fail';
            
            console.log(`${icon} ${test.name}: ${result.ratio}:1`);
        });
        
        console.groupEnd();
    }
};

// Auto-run audit in development mode
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    document.addEventListener('DOMContentLoaded', function() {
        // Wait 1 second for page to fully render
        setTimeout(() => {
            ColorContrastChecker.testDesignSystemColors();
            
            // Optionally run full page audit (can be verbose)
            // ColorContrastChecker.generateReport();
        }, 1000);
    });
}

// Export to global scope for manual testing
window.ColorContrastChecker = ColorContrastChecker;

// Console helper
console.log('💡 Color Contrast Checker loaded. Use ColorContrastChecker.generateReport() to audit the page.');
