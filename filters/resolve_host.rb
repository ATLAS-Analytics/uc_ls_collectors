require 'socket'

def lookup_hostname(ip)
    result = {
        'client' => ''   
    }
    begin
        result['client'] = Socket.gethostbyaddr(IPAddr.new(ip).hton).first
    rescue SocketError
    end
    return result
end

def filter(event)
    
    event.set("source", lookup_hostname(event.get("ip")) ) unless event.get("source")

    return [event]
end