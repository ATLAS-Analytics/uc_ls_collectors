require 'socket'
require 'resolv'

def get_ips(address)
    result = {
        'ipv4' => nil,
        'hostname_v4' => nil,
        'ipv6' => nil,
        'hostname_v6' => nil
    }
    is_hostname = !Regexp.union([Resolv::IPv4::Regex, Resolv::IPv6::Regex]).match?(address)
    
    begin
        #note: reverse lookups with getaddrinfo don't seem to consistently work so don't even bother
        addrinfo = Socket.getaddrinfo(address, nil)
        addrinfo.each do |ai|
            if ai[0] == 'AF_INET' then
                result['ipv4'] = ai[3]
                #result['hostname_v4'] = ai[2]
            elsif ai[0] == 'AF_INET6' then
                result['ipv6'] = ai[3]
                #remove scope id since not compatible with elastic ip type
                result['ipv6'] = result['ipv6'].gsub(/%\d+?/,"")
                #result['hostname_v6'] = ai[2]
            end
        end
    rescue
    end
    
    #do reverse lookups after we settled on addresses
    # if we were given a hostname, just use that
    if result['ipv4'] then
        begin
            if is_hostname then
                result['hostname_v4'] = address
            else
                result['hostname_v4'] = Resolv.new.getname result['ipv4']
            end
        rescue
        end
    end
    if result['ipv6'] then
        begin
            if is_hostname then
                result['hostname_v6'] = address
            else
                result['hostname_v6'] = Resolv.new.getname result['ipv6']
            end
        rescue
        end
    end
    
    return result
end


def filter(event)
    # hs = event.get('[result][paths]')
    # c = 1
    # hops = []
    # ttls = []
    # asns = []
    # rtts = []
    # hs.each do |h|
    #     hops.push(h["ip"])
    #     ttls.push(c)
    #     asns.push(h["as"]["number"])
    #     rtts.push(h["rtt"][2,6].to_f)
    #     c = c + 1
    # end
    event.set('ingest_timestamp', Time.now.utc.to_f * 1000)
    return [event]
end