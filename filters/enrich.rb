require 'socket'
require 'resolv'

def get_ips(address)
    result = {
        'ipv4' => nil,
        'ipv6' => nil
    }
    is_hostname = !Regexp.union([Resolv::IPv4::Regex, Resolv::IPv6::Regex]).match?(address)
    
    begin
        addrinfo = Socket.getaddrinfo(address, nil)
        addrinfo.each do |ai|
            if ai[0] == 'AF_INET' then
                result['ipv4'] = ai[3]
            elsif ai[0] == 'AF_INET6' then
                result['ipv6'] = ai[3]
                #remove scope id since not compatible with elastic ip type
                result['ipv6'] = result['ipv6'].gsub(/%\d+?/,"")
            end
        end
    rescue
    end
    
    return result
end

def filter(event)
    
    event.set("source", get_ips(event.get("src_host")) ) unless event.get("source")
    event.set("destination", get_ips(event.get("dest_host"))) unless event.get("destination")

    return [event]
end