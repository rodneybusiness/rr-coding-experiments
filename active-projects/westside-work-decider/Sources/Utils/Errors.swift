import Foundation

// MARK: - Domain Error Types

/// Errors that can occur when loading or processing spot data
enum SpotDataError: LocalizedError {
    case missingBundleResource(name: String)
    case decodingFailed(underlying: Error)
    case fileNotFound(path: String)
    case emptyDataset
    case corruptedUserState(underlying: Error)

    var errorDescription: String? {
        switch self {
        case .missingBundleResource(let name):
            return "Could not find '\(name)' in the app bundle"
        case .decodingFailed(let error):
            return "Failed to parse spot data: \(error.localizedDescription)"
        case .fileNotFound(let path):
            return "File not found at: \(path)"
        case .emptyDataset:
            return "No spots found in the dataset"
        case .corruptedUserState(let error):
            return "Your saved preferences may be corrupted: \(error.localizedDescription)"
        }
    }

    var recoverySuggestion: String? {
        switch self {
        case .missingBundleResource:
            return "Try reinstalling the app"
        case .decodingFailed:
            return "The data format may have changed. Try updating the app"
        case .fileNotFound:
            return "Ensure the data file exists at the specified location"
        case .emptyDataset:
            return "Check if the data file contains valid entries"
        case .corruptedUserState:
            return "Your favorites and history will be reset"
        }
    }
}

/// Errors that can occur with AI recommendation services
enum AIServiceError: LocalizedError {
    case missingAPIKey
    case invalidResponse(details: String)
    case networkError(underlying: Error)
    case timeout
    case rateLimited(retryAfter: TimeInterval?)
    case serverError(statusCode: Int)
    case parsingFailed(underlying: Error)

    var errorDescription: String? {
        switch self {
        case .missingAPIKey:
            return "OpenAI API key not configured"
        case .invalidResponse(let details):
            return "Invalid response from AI service: \(details)"
        case .networkError(let error):
            return "Network error: \(error.localizedDescription)"
        case .timeout:
            return "Request timed out"
        case .rateLimited(let retryAfter):
            if let seconds = retryAfter {
                return "Rate limited. Try again in \(Int(seconds)) seconds"
            }
            return "Rate limited. Please try again later"
        case .serverError(let code):
            return "Server error (HTTP \(code))"
        case .parsingFailed(let error):
            return "Failed to parse AI response: \(error.localizedDescription)"
        }
    }

    var recoverySuggestion: String? {
        switch self {
        case .missingAPIKey:
            return "Set OPENAI_API_KEY environment variable or use offline mode"
        case .invalidResponse:
            return "Try rephrasing your question"
        case .networkError:
            return "Check your internet connection and try again"
        case .timeout:
            return "The service is slow. Try again or use offline recommendations"
        case .rateLimited:
            return "You've made too many requests. Wait a moment and try again"
        case .serverError:
            return "The AI service is experiencing issues. Try again later"
        case .parsingFailed:
            return "Try a simpler question"
        }
    }

    var isRetryable: Bool {
        switch self {
        case .networkError, .timeout, .serverError:
            return true
        case .rateLimited(let retryAfter):
            return retryAfter != nil
        default:
            return false
        }
    }
}

/// Errors related to location services
enum LocationError: LocalizedError {
    case permissionDenied
    case permissionRestricted
    case serviceDisabled
    case locationUnknown
    case geocodingFailed(underlying: Error)

    var errorDescription: String? {
        switch self {
        case .permissionDenied:
            return "Location access was denied"
        case .permissionRestricted:
            return "Location access is restricted on this device"
        case .serviceDisabled:
            return "Location services are disabled"
        case .locationUnknown:
            return "Unable to determine your location"
        case .geocodingFailed(let error):
            return "Failed to find location: \(error.localizedDescription)"
        }
    }

    var recoverySuggestion: String? {
        switch self {
        case .permissionDenied:
            return "Enable location access in Settings > Privacy > Location Services"
        case .permissionRestricted:
            return "Contact your device administrator"
        case .serviceDisabled:
            return "Enable Location Services in Settings"
        case .locationUnknown:
            return "Move to an area with better GPS signal"
        case .geocodingFailed:
            return "Check your internet connection and try again"
        }
    }
}

// MARK: - Loading State

/// Represents the loading state of async operations
enum LoadingState<T> {
    case idle
    case loading
    case loaded(T)
    case failed(Error)

    var isLoading: Bool {
        if case .loading = self { return true }
        return false
    }

    var value: T? {
        if case .loaded(let value) = self { return value }
        return nil
    }

    var error: Error? {
        if case .failed(let error) = self { return error }
        return nil
    }

    var hasLoaded: Bool {
        if case .loaded = self { return true }
        return false
    }
}

// MARK: - Result Builder for Error Recovery

/// A helper for chaining fallback operations
struct ErrorRecovery<T> {
    private let operation: () async throws -> T
    private var fallbacks: [() async throws -> T] = []

    init(_ operation: @escaping () async throws -> T) {
        self.operation = operation
    }

    func fallback(_ alternative: @escaping () async throws -> T) -> ErrorRecovery<T> {
        var copy = self
        copy.fallbacks.append(alternative)
        return copy
    }

    func execute() async throws -> T {
        do {
            return try await operation()
        } catch {
            for fallback in fallbacks {
                do {
                    return try await fallback()
                } catch {
                    continue
                }
            }
            throw error
        }
    }
}

// MARK: - User-Facing Error Display

/// A user-friendly error representation for display in UI
struct DisplayableError: Identifiable {
    let id = UUID()
    let title: String
    let message: String
    let suggestion: String?
    let isRetryable: Bool
    let retryAction: (() -> Void)?

    init(from error: Error, retryAction: (() -> Void)? = nil) {
        if let localizedError = error as? LocalizedError {
            self.title = "Something went wrong"
            self.message = localizedError.errorDescription ?? error.localizedDescription
            self.suggestion = localizedError.recoverySuggestion
        } else {
            self.title = "Error"
            self.message = error.localizedDescription
            self.suggestion = nil
        }

        if let aiError = error as? AIServiceError {
            self.isRetryable = aiError.isRetryable
        } else {
            self.isRetryable = retryAction != nil
        }
        self.retryAction = retryAction
    }

    init(title: String, message: String, suggestion: String? = nil, isRetryable: Bool = false, retryAction: (() -> Void)? = nil) {
        self.title = title
        self.message = message
        self.suggestion = suggestion
        self.isRetryable = isRetryable
        self.retryAction = retryAction
    }
}
