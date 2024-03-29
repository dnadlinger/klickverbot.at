# Author: Brandon Mathis
# Description: Provides plugins with a method for wrapping and unwrapping input to prevent Markdown and Textile from parsing it.
# Purpose: This is useful for preventing Markdown and Textile from being too aggressive and incorrectly parsing in-line HTML.
module TemplateWrapper
  # Wrap input with a <div>
  def safe_wrap(input)
    #"<notextile><div class='bogus-wrapper'>#{input}</div></notextile>"
    input
  end
  # This must be applied after the
  def unwrap(input)
    #input.gsub /<notextile><div class='bogus-wrapper'>(.+?)<\/div><\/notextile>/m do
    #  $1
    #end
    input
  end
end

# Author: phaer, https://github.com/phaer
# Source: https://gist.github.com/1020852
# Description: Raw tag for jekyll. Keeps liquid from parsing text betweeen {% raw %} and {% endraw %}

module Jekyll
  class RawTag < Liquid::Block
    def parse(tokens)
      @nodelist ||= []
      @nodelist.clear

      while token = tokens.shift
        if token =~ FullToken
          if block_delimiter == $1
            end_tag
            return
          end
        end
        @nodelist << token if not token.empty?
      end
    end
  end
end

Liquid::Template.register_tag('raw', Jekyll::RawTag)
