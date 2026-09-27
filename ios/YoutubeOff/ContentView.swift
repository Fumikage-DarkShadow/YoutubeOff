import SwiftUI
import AVKit
import UniformTypeIdentifiers

struct ContentView: View {
    @EnvironmentObject private var library: VideoLibrary
    @State private var downloader: DownloadManager?
    @State private var link = ""
    @State private var showImporter = false
    @State private var selectedVideo: VideoItem?

    var body: some View {
        NavigationStack {
            List {
                Section("Ajouter une vidéo") {
                    TextField("Lien direct vers un fichier vidéo", text: $link, axis: .vertical)
                        .textInputAutocapitalization(.never)
                        .keyboardType(.URL)
                        .autocorrectionDisabled()
                    Button("Télécharger sur cet iPhone") {
                        downloader?.download(link)
                    }
                    .buttonStyle(.borderedProminent)
                    .disabled(link.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)

                    if let downloader, !downloader.status.isEmpty {
                        VStack(alignment: .leading, spacing: 6) {
                            Text(downloader.status)
                            ProgressView(value: downloader.progress)
                        }
                    }
                    if let error = downloader?.errorMessage {
                        Text(error).foregroundStyle(.red)
                    }
                    Button("Importer depuis Fichiers") { showImporter = true }
                }

                Section("Sur cet iPhone") {
                    if library.items.isEmpty {
                        ContentUnavailableView("Aucune vidéo", systemImage: "film", description: Text("Les fichiers ajoutés ici resteront disponibles sans réseau."))
                    } else {
                        ForEach(library.items) { item in
                            Button { selectedVideo = item } label: {
                                HStack {
                                    Image(systemName: "play.rectangle.fill").font(.title2).foregroundStyle(.red)
                                    VStack(alignment: .leading) {
                                        Text(item.title).foregroundStyle(.primary)
                                        Text("\(ByteCountFormatter.string(fromByteCount: item.size, countStyle: .file)) · Hors ligne")
                                            .font(.caption).foregroundStyle(.secondary)
                                    }
                                }
                            }
                        }
                        .onDelete { offsets in
                            offsets.map { library.items[$0] }.forEach(library.delete)
                        }
                    }
                }
            }
            .navigationTitle("YoutubeOff")
            .fileImporter(isPresented: $showImporter, allowedContentTypes: [.movie, .mpeg4Movie, .video]) { result in
                guard case let .success(url) = result else { return }
                let allowed = url.startAccessingSecurityScopedResource()
                defer { if allowed { url.stopAccessingSecurityScopedResource() } }
                let temporary = FileManager.default.temporaryDirectory.appendingPathComponent(url.lastPathComponent)
                do {
                    try? FileManager.default.removeItem(at: temporary)
                    try FileManager.default.copyItem(at: url, to: temporary)
                    try library.add(fileURL: temporary)
                } catch { downloader?.errorMessage = error.localizedDescription }
            }
            .sheet(item: $selectedVideo) { item in
                VideoPlayer(player: AVPlayer(url: item.fileURL))
                    .ignoresSafeArea()
            }
        }
        .task {
            if downloader == nil { downloader = DownloadManager(library: library) }
        }
    }
}
