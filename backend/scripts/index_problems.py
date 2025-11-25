"""
Problem Bank Indexing Script

Scans backend/data/problems/ directory for JSON problem files,
parses them, and creates a unified index for fast lookup.

Output: backend/data/extracted/problems_index.json
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def scan_problem_files(problems_dir: str) -> List[Path]:
    """Scan directory for JSON problem files."""
    problems_path = Path(problems_dir)

    if not problems_path.exists():
        print(f"❌ Problems directory not found: {problems_dir}")
        return []

    json_files = list(problems_path.glob("*.json"))
    print(f"✅ Found {len(json_files)} JSON files")
    return json_files


def parse_problem_file(file_path: Path) -> List[Dict[str, Any]]:
    """Parse a single problem JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Handle different JSON structures
        if isinstance(data, list):
            problems = data
        elif isinstance(data, dict):
            # If it's a dict, check for common keys
            if 'problems' in data:
                problems = data['problems']
            else:
                # Treat the entire dict as a single problem
                problems = [data]
        else:
            print(f"⚠️  Unexpected format in {file_path.name}")
            return []

        print(f"  📄 {file_path.name}: {len(problems)} problems")
        return problems

    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error in {file_path.name}: {e}")
        return []
    except Exception as e:
        print(f"❌ Error reading {file_path.name}: {e}")
        return []


def normalize_problem(problem: Dict[str, Any], file_source: str, index: int) -> Dict[str, Any]:
    """Normalize problem structure to consistent format."""

    # Generate ID if not present
    problem_id = problem.get('id', f"prob_{file_source}_{index:03d}")

    # Extract fields with fallbacks
    normalized = {
        "id": problem_id,
        "topic": problem.get('topic', problem.get('subject', 'physics')).lower(),
        "difficulty": problem.get('difficulty', problem.get('level', 'medium')).lower(),
        "question": problem.get('question', problem.get('problem', problem.get('text', ''))),
        "solution": problem.get('solution', problem.get('answer_explanation', '')),
        "hints": problem.get('hints', problem.get('hint', [])),
        "answer": problem.get('answer', problem.get('correct_answer', '')),
        "source_file": file_source
    }

    # Ensure hints is a list
    if isinstance(normalized['hints'], str):
        normalized['hints'] = [normalized['hints']]
    elif not isinstance(normalized['hints'], list):
        normalized['hints'] = []

    return normalized


def create_index(problems: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create indexed structure with statistics."""

    # Count by topic
    topics = {}
    for p in problems:
        topic = p['topic']
        topics[topic] = topics.get(topic, 0) + 1

    # Count by difficulty
    difficulties = {}
    for p in problems:
        diff = p['difficulty']
        difficulties[diff] = difficulties.get(diff, 0) + 1

    index = {
        "generated_at": datetime.now().isoformat(),
        "total_problems": len(problems),
        "topics": topics,
        "difficulties": difficulties,
        "problems": problems
    }

    return index


def save_index(index: Dict[str, Any], output_path: str):
    """Save index to JSON file."""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Index saved to: {output_path}")
    print(f"   Total problems: {index['total_problems']}")
    print(f"   Topics: {len(index['topics'])}")
    print(f"   Difficulties: {len(index['difficulties'])}")


def create_sample_problems():
    """Create sample problems if no problems directory exists."""
    sample_problems = [
        {
            "id": "kinematics_001",
            "topic": "kinematics",
            "difficulty": "easy",
            "question": "A car moves with a constant velocity of 20 m/s. How far does it travel in 5 seconds?",
            "solution": "Using distance = velocity × time: d = 20 m/s × 5 s = 100 m",
            "hints": [
                "Use the formula: distance = velocity × time",
                "Make sure units are consistent"
            ],
            "answer": "100 m"
        },
        {
            "id": "dynamics_001",
            "topic": "dynamics",
            "difficulty": "medium",
            "question": "A block of mass 5 kg is pushed with a force of 20 N. If there is no friction, what is the acceleration?",
            "solution": "Using Newton's second law F = ma: a = F/m = 20 N / 5 kg = 4 m/s²",
            "hints": [
                "Use Newton's second law: F = ma",
                "Rearrange to find acceleration: a = F/m"
            ],
            "answer": "4 m/s²"
        },
        {
            "id": "energy_001",
            "topic": "energy",
            "difficulty": "medium",
            "question": "A ball of mass 0.5 kg is thrown upward with an initial velocity of 10 m/s. What is its initial kinetic energy? (g = 10 m/s²)",
            "solution": "Using KE = (1/2)mv²: KE = 0.5 × 0.5 kg × (10 m/s)² = 25 J",
            "hints": [
                "Use the kinetic energy formula: KE = (1/2)mv²",
                "Square the velocity before multiplying"
            ],
            "answer": "25 J"
        }
    ]

    return sample_problems


def main():
    """Main indexing process."""
    print("=" * 60)
    print("JEE-Helper: Problem Bank Indexing")
    print("=" * 60)

    # Determine base directory
    script_dir = Path(__file__).parent
    backend_dir = script_dir.parent
    problems_dir = backend_dir / "data" / "problems"
    output_path = backend_dir / "data" / "extracted" / "problems_index.json"

    print(f"\nScanning: {problems_dir}")

    # Check if problems directory exists and create sample problems if empty
    problems_dir.mkdir(parents=True, exist_ok=True)

    # Scan for problem files
    problem_files = scan_problem_files(problems_dir)

    if not problem_files:
        print(f"\nNo problem files found. Creating sample problems for testing...")

        # Save sample problems
        sample_file = problems_dir / "sample_problems.json"
        with open(sample_file, 'w', encoding='utf-8') as f:
            json.dump(create_sample_problems(), f, indent=2, ensure_ascii=False)

        print(f"✅ Created {sample_file}")

        # Rescan
        problem_files = scan_problem_files(problems_dir)

    # Parse all problems
    print("\n📖 Parsing problem files...")
    all_problems = []

    for file_path in problem_files:
        problems = parse_problem_file(file_path)
        file_source = file_path.stem

        for idx, problem in enumerate(problems):
            normalized = normalize_problem(problem, file_source, idx)
            all_problems.append(normalized)

    print(f"\n✅ Total problems parsed: {len(all_problems)}")

    # Create index
    print("\n📊 Creating index...")
    index = create_index(all_problems)

    # Display statistics
    print("\n📈 Statistics:")
    print(f"  Topics:")
    for topic, count in sorted(index['topics'].items()):
        print(f"    - {topic}: {count}")

    print(f"  Difficulties:")
    for diff, count in sorted(index['difficulties'].items()):
        print(f"    - {diff}: {count}")

    # Save index
    save_index(index, output_path)

    print("\n" + "=" * 60)
    print("✅ Indexing complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
