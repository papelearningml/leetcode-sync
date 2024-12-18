class Logger:
    def __init__(self):
        self.current_problem = None

    def start_problem(self, title):
        print("\n" + "="*80)
        print(f"📝 Processing: {title}")
        print("="*80)
        self.current_problem = title

    def info(self, message):
        print(f"  ℹ️ {message}")

    def success(self, message):
        print(f"  ✅ {message}")

    def warning(self, message):
        print(f"  ⚠️ {message}")

    def error(self, message):
        print(f"  ❌ {message}")

    def summary(self, updated_problems, skipped_problems):
        print("\n" + "="*80)
        print("📊 Synchronization Summary")
        print("="*80)
        if updated_problems:
            print("\n✅ Updated problems:")
            for problem in updated_problems:
                print(f"  • {problem}")
        if skipped_problems:
            print("\n⏩ Skipped problems (no changes):")
            for problem in skipped_problems:
                print(f"  • {problem}")