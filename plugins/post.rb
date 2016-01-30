Jekyll::Hooks.register :posts, :pre_render do |post, payload|
  post.data['nonempty_tags'] =
    post.data['tags'].reject { |t| post.site.tags[t].count <= 1 }
end
