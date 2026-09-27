import Foundation

@MainActor
final class DownloadManager: NSObject, ObservableObject {
    @Published var progress: Double = 0
    @Published var status = ""
    @Published var errorMessage: String?

    private weak var library: VideoLibrary?
    private var session: URLSession!
    private var suggestedFileName = "video.mp4"

    init(library: VideoLibrary) {
        self.library = library
        super.init()
        let configuration = URLSessionConfiguration.background(withIdentifier: "com.youtubeoff.downloads")
        configuration.allowsCellularAccess = true
        session = URLSession(configuration: configuration, delegate: self, delegateQueue: .main)
    }

    func download(_ text: String) {
        errorMessage = nil
        guard let url = URL(string: text), ["http", "https"].contains(url.scheme?.lowercased() ?? "") else {
            errorMessage = "Colle un lien vidéo valide."
            return
        }
        suggestedFileName = url.lastPathComponent.isEmpty ? "video.mp4" : url.lastPathComponent
        status = "Téléchargement…"
        progress = 0
        session.downloadTask(with: url).resume()
    }
}

extension DownloadManager: URLSessionDownloadDelegate {
    nonisolated func urlSession(_ session: URLSession, downloadTask: URLSessionDownloadTask, didWriteData bytesWritten: Int64, totalBytesWritten: Int64, totalBytesExpectedToWrite: Int64) {
        guard totalBytesExpectedToWrite > 0 else { return }
        Task { @MainActor in
            progress = Double(totalBytesWritten) / Double(totalBytesExpectedToWrite)
        }
    }

    nonisolated func urlSession(_ session: URLSession, downloadTask: URLSessionDownloadTask, didFinishDownloadingTo location: URL) {
        Task { @MainActor in
            do {
                try library?.add(fileURL: location, suggestedName: suggestedFileName)
                status = "Enregistré sur l’iPhone"
                progress = 1
            } catch {
                errorMessage = "Impossible d’enregistrer ce fichier : \(error.localizedDescription)"
                status = ""
            }
        }
    }

    nonisolated func urlSession(_ session: URLSession, task: URLSessionTask, didCompleteWithError error: Error?) {
        guard let error else { return }
        Task { @MainActor in
            errorMessage = "Téléchargement interrompu : \(error.localizedDescription)"
            status = ""
        }
    }
}
