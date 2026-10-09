class LinguaFlowError(Exception):
    """Base application exception."""
    status_code = 500


class FileValidationError(LinguaFlowError):
    status_code = 400


class UnsupportedFormatError(FileValidationError):
    status_code = 415


class FileTooLargeError(FileValidationError):
    status_code = 413


class EngineUnavailableError(LinguaFlowError):
    status_code = 503


class TranslationError(LinguaFlowError):
    status_code = 500


class ExtractionError(LinguaFlowError):
    status_code = 422


class ReconstructionError(LinguaFlowError):
    status_code = 500


class RemoteEngineDisabledError(LinguaFlowError):
    status_code = 403
