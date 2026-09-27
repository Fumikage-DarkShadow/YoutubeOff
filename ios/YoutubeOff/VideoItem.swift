import Foundation

struct VideoItem: Identifiable, Codable, Equatable {
    let id: UUID
    let title: String
    let fileName: String
    let createdAt: Date
    let size: Int64

    var fileURL: URL {
        VideoLibrary.downloadsDirectory.appendingPathComponent(fileName)
    }
}

@MainActor
final class VideoLibrary: ObservableObject {
    static let downloadsDirectory: URL = {
        let folder = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("YoutubeOff", isDirectory: true)
        try? FileManager.default.createDirectory(at: folder, withIntermediateDirectories: true)
        return folder
    }()

    @Published private(set) var items: [VideoItem] = []
    private let indexURL = downloadsDirectory.appendingPathComponent("library.json")

    init() {
        load()
        removeMissingFiles()
    }

    func add(fileURL: URL, suggestedName: String? = nil) throws {
        let name = uniqueFileName(for: suggestedName ?? fileURL.lastPathComponent)
        let destination = Self.downloadsDirectory.appendingPathComponent(name)
        try FileManager.default.moveItem(at: fileURL, to: destination)
        let size = (try? destination.resourceValues(forKeys: [.fileSizeKey]).fileSize).map(Int64.init) ?? 0
        items.insert(VideoItem(id: UUID(), title: title(from: name), fileName: name, createdAt: .now, size: size), at: 0)
        save()
    }

    func delete(_ item: VideoItem) {
        try? FileManager.default.removeItem(at: item.fileURL)
        items.removeAll { $0.id == item.id }
        save()
    }

    private func load() {
        guard let data = try? Data(contentsOf: indexURL),
              let saved = try? JSONDecoder().decode([VideoItem].self, from: data) else { return }
        items = saved
    }

    private func save() {
        guard let data = try? JSONEncoder().encode(items) else { return }
        try? data.write(to: indexURL, options: .atomic)
    }

    private func removeMissingFiles() {
        items.removeAll { !FileManager.default.fileExists(atPath: $0.fileURL.path) }
        save()
    }

    private func uniqueFileName(for proposed: String) -> String {
        let safe = proposed.replacingOccurrences(of: "/", with: "-")
        let stem = (safe as NSString).deletingPathExtension
        let ext = (safe as NSString).pathExtension
        var index = 1
        var candidate = safe
        while FileManager.default.fileExists(atPath: Self.downloadsDirectory.appendingPathComponent(candidate).path) {
            index += 1
            candidate = "\(stem) (\(index)).\(ext)"
        }
        return candidate
    }

    private func title(from fileName: String) -> String {
        (fileName as NSString).deletingPathExtension.replacingOccurrences(of: "_", with: " ")
    }
}
