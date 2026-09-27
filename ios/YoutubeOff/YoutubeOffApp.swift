import SwiftUI

@main
struct YoutubeOffApp: App {
    @StateObject private var library = VideoLibrary()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(library)
        }
    }
}
