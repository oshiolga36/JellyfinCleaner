# Jellyfin Library Master Tool (JLMT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**JLMT** is a professional-grade suite designed to automate the curation of large-scale media libraries. It bridges the gap between raw file acquisition and a polished streaming experience by enforcing strict naming conventions and eliminating redundancy.



## 🛠 Technical Core Features

### 1. Multi-Threaded I/O Operations
Designed for high-latency environments (NAS/SMB shares). The UI operates on a separate thread from the file-system walker, ensuring a responsive interface during deep-hash scans of terabyte-scale libraries.

### 2. MD5 Bit-Stream Deduplication
Unlike standard name-based detectors, JLMT calculates an MD5 checksum of the file headers. This identifies identical media assets even if filenames have been altered or obfuscated.

### 3. Non-Destructive Isolation (Safety-First)
The tool follows a **Zero-Data-Loss** policy. Instead of `os.remove()`, unverified files and confirmed duplicates are moved to an internal `_ISOLATED_JUNK` directory for manual audit.

### 4. Semantic Directory Restructuring
* **Movies:** Normalizes strings (regex-based) to extract titles and years, then renames the primary video container to match the parent directory.
* **TV Shows:** Consolidates season-specific fragments and merges directories based on string similarity.
* **Music:** Filters high-fidelity audio formats while preserving critical sidecar files like album art and synchronized lyrics.

## ⚙️ Module Specifications

| Module | Target Formats | Logic Applied |
| :--- | :--- | :--- |
| **Music** | `.flac, .mp3, .m4a` | Junk stripping, Hash-deduplication, Meta-preservation |
| **TV Shows** | `.mkv, .mp4, .vtt` | Directory merging, Regex cleaning, Recursive pruning |
| **Movies** | `.mkv, .mp4` | Pro-Rename (Title + Year), Primary asset identification |

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- `Tkinter` (included in most Python distributions)

### Execution
```bash
git clone [https://github.com/YOUR_USERNAME/jellyfin-master-tool.git](https://github.com/YOUR_USERNAME/jellyfin-master-tool.git)
cd jellyfin-master-tool
python jellyfin_master_tool.py
