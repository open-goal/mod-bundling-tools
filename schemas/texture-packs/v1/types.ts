type ValidTags = "enhancement" | "overhaul" | "highres" | "parody" | "themed" | "mods" | string;

export interface TexturePackMetadata {
    // valid semver
    schemaVersion: string,
    // valid semver
    version: string,
    name: string,
    description: string,
    authors: string,
    publishedDate: string,
    tags: ValidTags[]
}