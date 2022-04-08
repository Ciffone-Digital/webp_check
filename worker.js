/**
 * Listens for requests and serves the webp version of images.
 * Written to be used with Cloudflare workers. Modify as needed for your application.
 */

 addEventListener('fetch', event => {
    event.respondWith(serveWebp(event.request))
})

async function serveWebp(request) {

    let regex = /\.jpeg$|\.jpg$|\.png$/

    if(request.headers.get('Accept')
        && request.headers.get('Accept').match(/image\/webp/)
        && request.url.match(regex)) {
      
        let url = new URL(request.url.replace(regex, '.webp'))

        const modifiedRequest = new Request(url, {
            method: request.method,
            headers: request.headers
        })

        const webpResponse = await fetch(modifiedRequest)

        const webpHeaders = new Headers(webpResponse.headers)
        webpHeaders.append('X-WebWorker', 'active')

        return new Response(webpResponse.body, {
            status: webpResponse.status,
            statusText: webpResponse.statusText,
            headers: webpHeaders
        })

    } else {
        const response = await fetch(request)
        return response
    }
}