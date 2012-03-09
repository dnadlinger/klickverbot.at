#custom filters for Octopress
require './plugins/post_filters'
require './plugins/raw'

module OctopressFilters
  include TemplateWrapper
  def post_filter(input)
    unwrap(input)
  end
end

module Jekyll
  class ContentFilters < PostFilter
    include OctopressFilters
    def post_render(post)
      post.content = post_filter(post.content)
    end
  end
end

module CustomLiquidFilters
  def strip_html(input)
    input.gsub(%r{</?[^>]+?>}, '')
  end
end
Liquid::Template.register_filter CustomLiquidFilters
