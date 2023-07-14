// interface ChangelogEntry {
//     summary: string,
//     timestamp: string,
//     authors?: string[],
//     description?: string,
// }

type ValidTags = "challenge" | "rng" | "gameplay" | "speedrunning" | "textures" | "beta" | "multiplayer" | "practice" | "custom-enemy";

export interface ModMetadata {
    // valid semver
    schemaVersion: string,
    // valid semver
    version: string,
    name: string,
    description: string,
    authors: string[],
    // changelog: ChangelogEntry[], TODO eventually
    tags: ValidTags[],
    publishedDate: string,
    websiteUrl?: string
}