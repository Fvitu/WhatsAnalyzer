"""Utility functions for file handling and validation."""

import os
import hashlib
from werkzeug.utils import secure_filename

# Optional import - python-magic requires native libmagic library
try:
    import magic

    MAGIC_AVAILABLE = True
except (ImportError, OSError):
    MAGIC_AVAILABLE = False


class FileValidator:
    """Validate uploaded files for security and size constraints."""

    def __init__(self, allowed_extensions=None, max_size_bytes=None):
        """
        Initialize validator.

        Args:
            allowed_extensions: Set of allowed file extensions
            max_size_bytes: Maximum file size in bytes
        """
        self.allowed_extensions = allowed_extensions or {"txt"}
        self.max_size_bytes = max_size_bytes or (10 * 1024 * 1024)  # 10MB default

    def validate_extension(self, filename):
        """
        Check if file has an allowed extension.

        Args:
            filename: Name of the file

        Returns:
            bool: True if extension is allowed
        """
        if not filename or "." not in filename:
            return False

        ext = filename.rsplit(".", 1)[1].lower()
        return ext in self.allowed_extensions

    def validate_size(self, file_stream):
        """
        Check if file size is within limits.

        Args:
            file_stream: File stream object

        Returns:
            tuple: (is_valid, size_in_bytes)
        """
        # Seek to end to get size
        file_stream.seek(0, os.SEEK_END)
        size = file_stream.tell()
        file_stream.seek(0)  # Reset to beginning

        return size <= self.max_size_bytes, size

    def validate_mime_type(self, file_stream):
        """
        Validate file MIME type (text/plain for .txt files).

        Args:
            file_stream: File stream object

        Returns:
            tuple: (is_valid, mime_type)
        """
        try:
            # Read first 2048 bytes for MIME detection
            file_stream.seek(0)
            header = file_stream.read(2048)
            file_stream.seek(0)

            # Use python-magic if available
            if MAGIC_AVAILABLE:
                try:
                    mime = magic.from_buffer(header, mime=True)
                except Exception:
                    # Fallback if magic fails
                    mime = self._simple_text_detection(header)
            else:
                # Fallback: simple text detection when magic not available
                mime = self._simple_text_detection(header)

            # Allow text files
            is_valid = mime.startswith("text/") or mime == "application/octet-stream"
            return is_valid, mime

        except Exception as e:
            # If detection fails, be conservative
            return False, "unknown"

    def _simple_text_detection(self, data):
        """
        Simple text file detection fallback when magic is not available.

        Args:
            data: Bytes to analyze

        Returns:
            str: MIME type
        """
        try:
            # Try to decode as UTF-8 or Latin-1
            try:
                data.decode("utf-8")
                return "text/plain"
            except UnicodeDecodeError:
                try:
                    data.decode("latin-1")
                    return "text/plain"
                except:
                    return "application/octet-stream"
        except:
            return "application/octet-stream"

    def sanitize_filename(self, filename):
        """
        Sanitize filename for secure storage.

        Args:
            filename: Original filename

        Returns:
            str: Sanitized filename
        """
        # Use werkzeug's secure_filename
        safe_name = secure_filename(filename)

        # Additional sanitization
        if not safe_name or safe_name == "":
            safe_name = "unnamed.txt"

        # Ensure it has .txt extension
        if not safe_name.endswith(".txt"):
            safe_name += ".txt"

        return safe_name

    def validate_file(self, file_obj):
        """
        Comprehensive file validation.

        Args:
            file_obj: Flask file object from request.files

        Returns:
            tuple: (is_valid, error_message, metadata)
        """
        metadata = {}

        # Check if file exists
        if not file_obj or file_obj.filename == "":
            return False, "No file selected", metadata

        # Validate extension
        if not self.validate_extension(file_obj.filename):
            return (
                False,
                f'File extension not allowed. Only {", ".join(self.allowed_extensions)} allowed',
                metadata,
            )

        # Validate size
        is_valid_size, size = self.validate_size(file_obj.stream)
        metadata["size"] = size

        if not is_valid_size:
            max_mb = self.max_size_bytes / (1024 * 1024)
            return False, f"File too large. Maximum size: {max_mb:.1f}MB", metadata

        # Validate MIME type
        is_valid_mime, mime_type = self.validate_mime_type(file_obj.stream)
        metadata["mime_type"] = mime_type

        if not is_valid_mime:
            return (
                False,
                f"Invalid file type. Expected text file, got {mime_type}",
                metadata,
            )

        # Sanitize filename
        safe_filename = self.sanitize_filename(file_obj.filename)
        metadata["safe_filename"] = safe_filename

        return True, None, metadata


def compute_file_hash(content, algorithm="sha256"):
    """
    Compute hash of file content for deduplication.

    Args:
        content: File content (string or bytes)
        algorithm: Hash algorithm to use

    Returns:
        str: Hex digest of hash
    """
    if isinstance(content, str):
        content = content.encode("utf-8")

    hasher = hashlib.new(algorithm)
    hasher.update(content)
    return hasher.hexdigest()


def format_file_size(size_bytes):
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        str: Formatted size (e.g., "1.5 MB")
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
