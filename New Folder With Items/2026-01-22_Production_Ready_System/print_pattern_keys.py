from scheduling.management.commands.apply_three_week_scw_sca_pattern import Command as PatternCommand
patterns = getattr(PatternCommand, 'patterns', {})
print(sorted(patterns.keys()))
