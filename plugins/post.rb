module Jekyll
  class Post
    def to_liquid(*args)
      self.data.deep_merge({
        "title"      => self.data["title"] || self.slug.split('-').select {|w| w.capitalize! || w }.join(' '),
        "url"        => self.url,
        "date"       => self.date,
        "id"         => self.id,
        "categories" => self.categories,
        "next"       => self.next,
        "previous"   => self.previous,
        "tags"       => self.tags,
        "nonempty_tags" => self.tags.reject { |t| self.site.tags[t].count <= 1 },
        "content"    => self.content
      })
    end
  end
end
